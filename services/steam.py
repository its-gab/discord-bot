import logging

import requests


logger = logging.getLogger(__name__)


WISHLIST_URL = (
    "https://api.steampowered.com/"
    "IWishlistService/GetWishlist/v1"
)

APP_DETAILS_URL = (
    "https://store.steampowered.com/api/appdetails"
)


def get_wishlist_discounts(
    steam_id: str,
    cc: str = "it",
    lang: str = "en"
):
    """
    Get discounted games from a Steam wishlist.

    Returns:
        list: discounted wishlist games
    """

    logger.info(
        "Checking Steam wishlist for %s",
        steam_id
    )

    # --------------------------------------------------
    # Get wishlist
    # --------------------------------------------------

    try:
        response = requests.get(
            WISHLIST_URL,
            params={
                "steamid": steam_id
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:
        logger.error(
            "Steam wishlist request failed: %s",
            error
        )
        return []

    except ValueError as error:
        logger.error(
            "Steam wishlist returned invalid JSON: %s",
            error
        )
        return []

    items = data.get(
        "response",
        {}
    ).get(
        "items",
        []
    )

    if not items:
        logger.info(
            "Wishlist empty, private, or invalid Steam ID."
        )
        return []

    appids = [
        str(item["appid"])
        for item in items
        if "appid" in item
    ]

    logger.info(
        "Found %d wishlist games.",
        len(appids)
    )

    # --------------------------------------------------
    # Get game details
    # --------------------------------------------------

    discounts = []

    for appid in appids:

        try:
            response = requests.get(
                APP_DETAILS_URL,
                params={
                    "appids": appid,
                    "cc": cc,
                    "l": lang,
                    "filters": "price_overview,basic"
                },
                timeout=10
            )

            response.raise_for_status()

            details = response.json()

        except requests.RequestException as error:
            logger.error(
                "Steam appdetails request failed "
                "for %s: %s",
                appid,
                error
            )
            continue

        except ValueError as error:
            logger.error(
                "Invalid JSON for app %s: %s",
                appid,
                error
            )
            continue

        # --------------------------------------------------
        # Validate response
        # --------------------------------------------------

        entry = details.get(appid)

        if not entry:
            continue

        if not entry.get("success"):
            continue

        game_data = entry.get(
            "data",
            {}
        )

        name = game_data.get(
            "name",
            "Unknown Game"
        )

        price_overview = game_data.get(
            "price_overview"
        )

        if not price_overview:
            continue

        # --------------------------------------------------
        # Check discount
        # --------------------------------------------------

        discount = price_overview.get(
            "discount_percent",
            0
        )

        if discount <= 0:
            continue

        discounts.append({
            "appid": int(appid),

            "name": name,

            "discount": discount,

            "original": (
                price_overview["initial"] / 100
            ),

            "final": (
                price_overview["final"] / 100
            )
        })

    # --------------------------------------------------
    # Sort by discount
    # --------------------------------------------------

    discounts.sort(
        key=lambda game: game["discount"],
        reverse=True
    )

    logger.info(
        "Found %d discounted wishlist games.",
        len(discounts)
    )

    return discounts