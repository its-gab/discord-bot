import asyncio
import discord
from discord.ext import commands

from services.fuel import trova_distributori


class Fuel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="!fuel [città | lat lon]"
    )
    async def fuel(self, ctx, *, posizione=None):

        embed = discord.Embed(
            title="⛽ Prezzi carburante",
            description="🔄 Sto cercando i distributori più convenienti...",
            color=discord.Color.orange()
        )

        message = await ctx.send(embed=embed)

        try:

            dati = await asyncio.to_thread(
                trova_distributori,
                posizione
            )

            embed = discord.Embed(
                title="⛽ Distributori più convenienti",
                color=discord.Color.green()
            )

            for carburante in ("Benzina", "Gasolio"):

                d = dati[carburante]

                if d is None:
                    embed.add_field(
                        name=carburante,
                        value="❌ Nessun distributore trovato entro il raggio impostato.",
                        inline=False
                    )
                    continue

                embed.add_field(
                    name=f"🚗 {carburante}",
                    value=(
                        f"**💶 Prezzo:** {d['Prezzo']:.3f} €/L\n"
                        f"**🏪 Bandiera:** {d['Bandiera']}\n"
                        f"**📍 Distanza:** {d['Distanza']} km\n"
                        f"**🏙️ Comune:** {d['Comune']} ({d['Provincia']})\n"
                        f"**🛣️ Indirizzo:** {d['Indirizzo']}\n"
                        f"**⛽ Self:** {'Sì' if d['Self'] else 'No'}\n"
                        f"**🕒 Aggiornato:** {d['DataAggiornamento']}"
                    ),
                    inline=False
                )

            await message.edit(embed=embed)

        except Exception as e:

            embed = discord.Embed(
                title="❌ Errore",
                description=str(e),
                color=discord.Color.red()
            )

            await message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(Fuel(bot))