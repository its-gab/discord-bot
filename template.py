from discord.ext import commands

class Template(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Event
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[Template] caricato ✔️")

    # Command
    @commands.command()
    async def test(self, ctx):
        await ctx.reply("Cog funzionante 🚀")


    # Command with argument
    @commands.command()
    async def say(self, ctx, *, text: str):
        await ctx.send(text)


# Setup
async def setup(bot):
    await bot.add_cog(Template(bot))