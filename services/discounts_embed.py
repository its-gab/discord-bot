import discord


def create_steam_embed(discounts):
    embed = discord.Embed(
        title="🎮 Steam Wishlist Discounts",
        description="Games from your wishlist currently on sale.",
        color=discord.Color.blurple()
    )

    if not discounts:
        embed.add_field(
            name="No discounts",
            value="There are currently no discounted games.",
            inline=False
        )

        return embed

    for game in discounts[:25]:
        name = game["name"]
        discount = game["discount"]
        original = game["original"]
        final = game["final"]
        appid = game["appid"]

        embed.add_field(
            name=name,
            value=(
                f"~~€{original:.2f}~~ → **€{final:.2f}** "
                f"• **-{discount}%**\n"
                f"[View on Steam](https://store.steampowered.com/app/{appid}/)"
            ),
            inline=False
        )

    return embed