import discord
from discord.ext import commands
from func import default


class Other(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['c'], help="Displays how the given color would look as an embed color.")
    async def color(self, ctx, hex):
        embed = discord.Embed(description = hex, color= int(hex, 16))
        embed.set_footer(text=default.footer())
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Other(client))