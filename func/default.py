limit = {
    'total': 6000,
    'title': 256,
    'description': 2048,
    'author': 256,
    'footer': 2048,
    'field': {
        'amount': 25,
        'name': 256,
        'value': 1024
    }
}

support_server = "[Support Server](https://discord.gg/JgR6XywMwZ)"
bot = "[Bot](https://top.gg/bot/795099690609279006)"

import typing

def footer(seperate : typing.Optional[bool] = False):
    if (seperate):
        return "| Connect 4 © 2021"
    return "Connect 4 © 2021"

def terminal():
    return 849531726312505355

import discord
from discord.ext import commands
from func.human import *

def profile(user : discord.User):
    return f"[{user.name}](https://discord.com/users/{user.id})"

class Embed:
    def __init__(self):
        self.client = commands.Bot

    def success(Title : str = None, Description : str = None, Author : discord.Member = None, Footer : str = None, Field : str = None):
        if not (Title): Title = "Success"
        if (Description): embed = discord.Embed(title=Title, description=Description, color = int(Color.green, 16))
        if (Author): embed.set_author(name=Author.name, icon_url=Author.avatar_url)
        if (Field):
            Field = Field.split('\s ')
            embed.add_field(name=Field[0], value=Field[1])
        FOOTER = footer()
        if (Footer):
            FOOTER = Footer + ' ' + footer(True)
        embed.set_footer(text=FOOTER)
        return embed

    def error(Title : str = None, Description : str = None, Footer : str = None, Field : str = None):
        if not (Title): Title = "Error"
        if (Description): embed = discord.Embed(title=Title, description=Description, color = int(Color.red, 16))
        if (Field):
            Field = Field.split('\s ')
            embed.add_field(name=Field[0], value=Field[1])
        FOOTER = footer()
        if (Footer):
            FOOTER = Footer + ' ' + footer(True)
        embed.set_footer(text=FOOTER)
        return embed

    def minimal(Title : str = None, Description : str = None, Color : typing.Optional[str] = "5261f8"):
        embed = discord.Embed(color=int(Color, 16))
        if (Title): embed = discord.Embed(title=Title, color=int(Color, 16))
        if (Description): embed = discord.Embed(description=Description, color=int(Color, 16))
        if (Title) and (Description): embed = discord.Embed(title=Title, description=Description, color=int(Color, 16))

        embed.set_footer(text=footer())
        return embed

    def custom(Title : str = None, Description : str = None, Color : typing.Optional[str] = "5261f8", Fields : list = [], Author : discord.Member = None, Footer : str = None, Image : str = None, Thumbnail : str = None):
        embed = discord.Embed(color=int(Color, 16))
        if (Title): embed = discord.Embed(title=Title, color=int(Color, 16))
        if (Description): embed = discord.Embed(description=Description, color=int(Color, 16))
        if (Title) and (Description): embed = discord.Embed(title=Title, description=Description, color=int(Color, 16))

        if (Author): embed.set_author(name=Author, icon_url=Author.avatar_url)
        if (Image): embed.set_image(url = Image)
        if (Thumbnail): embed.set_thumbnail(url=Thumbnail)
        FOOTER = footer()
        if (Footer):
            FOOTER = Footer + ' ' + footer(True)
        embed.set_footer(text=FOOTER)
        if (Fields):
            for FIELD in Fields:
                Field = FIELD.replace('\c', ',').split('\s ')
                embed.add_field(name = Field[0], value=Field[1], inline=bool(Field[2]))
        return embed

    async def maintenance(ctx):
        embed = discord.Embed(title="Maintenance", description=f"This command is currently under maintenance, visit the {B('[support server](https://discord.gg/JgR6XywMwZ)')} for further assistance.", color=int(Color.red, 16))
        embed.set_footer(text=footer())
        await ctx.send(embed=embed)


class Support_server:
    
    async def terminal(client, msg : typing.Union[discord.Embed, str]):
        channel = await commands.Bot.fetch_channel(client, 849531726312505355)
        if type(msg) == discord.Embed:
            await channel.send(embed=msg)
            return
        [await channel.send(str(msg)[i:i+2000]) for i in range(0, len(str(msg)), 2000)]


class Color:

    red = "c23b22"
    green = "03c03c"
    blurple = "5261f8"
    dark_grey = "36393f"
    white = "F0F0F0"
    grey = ""