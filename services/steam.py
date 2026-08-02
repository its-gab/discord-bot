import requests

def get_wishlist_discounts(steam_id):
    url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/wishlistdata/"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        wishlist = response.json()
    except requests.RequestException as e:
        print(f"[Steam Service] Request error: {e}")
        return []
    except ValueError as e:
        print(f"[Steam Service] Invalid JSON response: {e}")
        return []

    if not isinstance(wishlist, dict):
        print(f"[Steam Service] Unexpected wishlist format: {type(wishlist)} (empty/private wishlist?)")
        return []

    discounts = []

    for appid, game in wishlist.items():

        name = game.get("name", "Uknown Game")

        subs = game.get("subs")
        if not subs:
            continue

        price = subs[0]

        discount = price.get("discount_pct", 0)

        if discount > 0:
            discounts.append({
                "appid": int(appid),
                "name": name,
                "discount": discount,
                "original": price["price"] / 100,
                "final": price["discount_price"] / 100
            })

    return sorted(discounts, key=lambda x: x["discount"], reverse=True)