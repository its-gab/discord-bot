import discord

def create_steam_embed(discounts):
    embed = discord.Embed(
        title="🎮 Steam Wishlist",
        color=discord.Color.blue()
    )

    if not discounts:
        embed.description = "🎉 No games are currently on sale."
    else:
        embed.description = (
            f"There are **{len(discounts)}** games on sale!\n"
        )

        for game in discounts:
            embed.add_field(
                name=game["name"],
                value=(
                    f"💸 **-{game['discount']}%**\n"
                    f"~~{game['original']:.2f}€~~ → **{game['final']:.2f}€**\n"
                    f"[Open on Steam](https://store.steampowered.com/app/{game['appid']})"
                ),
                inline=False
            )

    embed.set_footer(text="Last checked")
    embed.timestamp = discord.utils.utcnow()

    return embed