import discord, asyncio
from discord.ext import commands
from func import default
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from func.human import *


class Other(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['bg'], help="Shows how a specific game background would look.")
    async def background(self, ctx, background):
        board = str(str(str(f'{background} ' * 7) + '\n') * 6)
        embed = discord.Embed(title = "Connect 4", description=f"Respond with {HL('1-7')} to play your move.\n{board}", color = 0xF0F0F0)
        embed.add_field(name=":blue_circle: Player 1", value = ctx.author.mention, inline=False)
        embed.add_field(name=":yellow_circle: Player 2", value = ctx.author, inline=False)
        embed.set_footer(text=f"ID: 0000000000000000 {default.footer(True)}")
        await ctx.send(embed=embed, delete_after=30)


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