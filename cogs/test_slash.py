import slash_util as slash


class Test_slash(slash.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash.slash_command(guild_id=843994109366501376)
    async def test(self, ctx : slash.Context):
        await ctx.send("testing slash commands", ephemeral=True)


def setup(bot):
    bot.add_cog(Test_slash(bot))
