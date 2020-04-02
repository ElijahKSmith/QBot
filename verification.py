import checks
from discord.ext import commands

class Verification(commands.Cog, name="Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.is_unverified)
    async def register(self, ctx):
        member = ctx.author.id
        await ctx.send("Not yet implemented")

def setup(bot):
    bot.add_cog(Verification(bot))

def teardown(bot):
    bot.remove_cog("Verification")