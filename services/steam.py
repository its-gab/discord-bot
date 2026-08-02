import requests

def get_wishlist_discounts(steam_id):
    url = f"https://store.steampowered.com/wishlist/profiles/{steam_id}/wishlistdata/"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Steam Service] Error: {e}")
        return []

    wishlist = response.json()
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