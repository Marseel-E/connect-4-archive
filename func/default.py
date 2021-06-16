import typing

def footer(seperate : typing.Optional[bool] = False):
    if (seperate):
        return "| Connect 4 © 2021"
    return "Connect 4 © 2021"

def developer():
    return [470866478720090114, 543937487580692493]

def terminal():
    return 849531726312505355

import discord
from discord.ext import commands
from func.human import *

class Embed:
    def __init__(self):
        self.client = commands.Bot

    def success(Title : str = None, Description : str = None, Author : discord.Member = None, Footer : str = None, Field : str = None):
        if not (Title): Title = "Success"
        if (Description): embed = discord.Embed(title=Title, description=Description, color = 0x03c03c)
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
        if (Description): embed = discord.Embed(title=Title, description=Description, color = 0xc23b22)
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
                Field = FIELD.split('\s ')
                embed.add_field(name = Field[0], value=Field[1], inline=Field[2])
        return embed

    def maintenance():
        embed = discord.Embed(title="Maintenance", description=f"This command is currently under maintenance, visit the {B('[support server](https://discord.gg/JgR6XywMwZ)')} for further assistance.", color=0x5261f8)
        embed.set_footer(text=footer())
        return embed