import discord, asyncio, random
from discord import player
from discord.ext import commands, tasks
from func import database as db
from func import default
from func.human import *


class Handler(commands.Cog):
    def __init__(self, client):
        self.client = client
        # self.matchmaking.start(self.client)


    # @tasks.loop(seconds=10)
    @commands.command(aliases=['mm'])
    @commands.is_owner()
    async def matchmaking(self, ctx):
        lobby = await db.Lobby.fetch()
        print(lobby)
        if len(lobby) < 2: return
        # Sort ranks & players
        newLobby = {}
        for rank in db.ranksData.keys():
            KL = [key for key, value in lobby.items() if value in db.ranksData.keys()]
            newLobby[rank] = KL

        print(newLobby)
        
        # Prepare game players
        p1 = 0; p2 = 0
        for rank in db.ranksData.keys():
            print(rank)
            player = random.randint(0, len(newLobby))
            print(player)
            try:
                if p1 == 0: p1 = self.client.fetch_user(int(newLobby[rank][player])); continue
                elif p2 == 0 and player != p1: p2 = self.client.fetch_user(int(newLobby[rank][player])); break
            except Exception:
                continue
        
        print(p1)
        print(p2)
        
        if p1 or p2 == 0: await ctx.send(f"Didn't find matching players"); return

        # Start game
        embed = default.Embed.success(None, f"{p1.mention}, {p2.mention} Prepare for your ranked game.")
        await p1.send(embed=embed); await p2.send(embed=embed)

        # Remove from lobby
        await db.Lobby.delete(p1.id); await db.Lobby.delete(p2.id)

        print(db.Lobby.data)


def setup(client):
    client.add_cog(Handler(client))