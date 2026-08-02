import requests
import time


def get_wishlist_discounts(steam_id, cc="it", lang="en"):
    wishlist_url = "https://api.steampowered.com/IWishlistService/GetWishlist/v1"
    try:
        resp = requests.get(wishlist_url, params={"steamid": steam_id}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[Steam Service] Request error (wishlist): {e}")
        return []
    except ValueError as e:
        print(f"[Steam Service] Invalid JSON response (wishlist): {e}")
        return []

    items = data.get("response", {}).get("items", [])
    if not items:
        print("[Steam Service] Wishlist vuota, privata, o steam_id non valido")
        return []

    appids = [str(item["appid"]) for item in items if "appid" in item]

    discounts = []

    for appid in appids:
        try:
            details_resp = requests.get(
                "https://store.steampowered.com/api/appdetails",
                params={"appids": appid, "cc": cc, "l": lang, "filters": "price_overview,basic"},
                timeout=10,
            )
            details_resp.raise_for_status()
            details = details_resp.json()
        except requests.RequestException as e:
            print(f"[Steam Service] Request error (appdetails {appid}): {e}")
            continue
        except ValueError as e:
            print(f"[Steam Service] Invalid JSON response (appdetails {appid}): {e}")
            continue

        entry = details.get(appid)
        if not entry or not entry.get("success"):
            continue

        game_data = entry.get("data", {})
        name = game_data.get("name", "Unknown Game")
        price_overview = game_data.get("price_overview")

        if not price_overview:
            continue

        discount = price_overview.get("discount_percent", 0)

        if discount > 0:
            discounts.append({
                "appid": int(appid),
                "name": name,
                "discount": discount,
                "original": price_overview["initial"] / 100,
                "final": price_overview["final"] / 100,
            })

    return sorted(discounts, key=lambda x: x["discount"], reverse=True)