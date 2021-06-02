import discord, typing
from discord.ext import commands
from func import database as db
from func.human import *
from func import default


class Handler(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    async def profile(self, ctx, member : typing.Optional[discord.Member]):
        user = ctx.author
        if (member):
            user = member
        data = await db.Get.user(user.id)
        embed = discord.Embed(color = int(data['embedColor'], 16))
        embed.set_author(name = user)
        embed.set_thumbnail(url = user.avatar_url)
        embed.add_field(name="Level:", value=data['level'], inline=True)
        embed.add_field(name="Rank:", value="Soon!", inline=True) #- Make rank
        embed.add_field(name=f"Games played: `({int(data['wins'] + data['draws'] + data['loses'])})`", value=f"**{data['wins']}** Wins | **{data['draws']}** Draws | **{data['loses']}** Loses", inline=False)
        embed.add_field(name="Primary disc:", value=f"{data['primaryDisc']} `{fix(data['primaryDisc'])}`", inline=True)
        embed.add_field(name="Secondary disc:", value=f"{data['secondaryDisc']} `{fix(data['secondaryDisc'])}`", inline=True)
        embed.add_field(name="Background:", value=f"{data['background']} `{fix(data['background'])}`", inline=False)
        embed.add_field(name="Embed color:", value=f"`{data['embedColor']}`", inline=False)
        embed.set_footer(text = f"Exp: {round(data['exp'])} / {round((data['level'] * 4.231) * 100)} {default.footer(True)}")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Handler(client))