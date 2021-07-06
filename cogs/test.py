import discord, asyncio, typing
from discord.ext import commands
from func import database as db
from func.human import *
from func import default
from func.default import limit

class Test(commands.Cog):
    def __init__(self, client):
        self.client = client
    




def setup(client):
    client.add_cog(Test(client))