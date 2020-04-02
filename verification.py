import checks
from discord.ext import commands

class Verification(commands.Cog, name="Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.is_unverified)
    @commands.guild_only()
    async def register(self, ctx):
        member = ctx.author.id
        await ctx.send("Not yet implemented")
        await ctx.send("Test")

    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('You cannot register, you may be already registered or currently in the verification process.')

def setup(bot):
    bot.add_cog(Verification(bot))

def teardown(bot):
    bot.remove_cog("Verification")