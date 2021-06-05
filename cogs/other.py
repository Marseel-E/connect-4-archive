import discord, asyncio
from discord.ext import commands
from func import default
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


class Other(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['c'], help="Displays how the given color would look as an embed color.")
    async def color(self, ctx, hex):
        embed = discord.Embed(description = hex, color= int(hex, 16))
        embed.set_footer(text=default.footer())
        await ctx.send(embed=embed)
    

    @commands.command(aliases=['rr'], help="Sends a rickroll GIF in the member's dm.")
    @commands.is_owner()
    async def rickroll(self, ctx, member : discord.Member):
        embed = discord.Embed(color=0x5261F8)
        embed.set_image(url='https://media.giphy.com/media/Ju7l5y9osyymQ/giphy.gif')
        await member.send(embed=embed)
        await ctx.message.delete()


def setup(client):
    DiscordComponents(client)
    client.add_cog(Other(client))