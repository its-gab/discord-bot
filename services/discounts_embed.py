import discord

def create_steam_embed(discounts):
    embed = discord.Embed(
        title="🎮 Steam Wishlist",
        color=discord.Color.blue()
    )

    if not discounts:
        embed.description = "🎉 Nessun gioco è attualmente in sconto."
    else:
        embed.description = (
            f"Ci sono **{len(discounts)}** giochi in sconto!\n"
        )

        for game in discounts:
            embed.add_field(
                name=game["name"],
                value=(
                    f"💸 **-{game['discount']}%**\n"
                    f"~~{game['original_price']:.2f}€~~ → **{game['discount_price']:.2f}€**\n"
                    f"[Apri su Steam](https://store.steampowered.com/app/{game['appid']})"
                ),
                inline=False
            )

    embed.set_footer(text="Ultimo controllo")
    embed.timestamp = discord.utils.utcnow()

    return embed