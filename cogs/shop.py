import discord, typing, asyncio
from discord.ext import commands
from func import database as db
from func.human import *
from func import default

class Handler(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['s', 'store'])
    async def shop(self, ctx, category : typing.Optional[str] = None):
        # Data
        data = await db.Fetch.items()
        invData = await db.Get.inventory(ctx.author.id)
        
        # Direct category
        if (category): pass
        
        # Main embed
        embed = discord.Embed(title="Connect 4 - Shop", description= ":blue_circle: Discs \n:white_circle: Backgrounds \n:orange_square: Embed colors", color = 0xFFD700)
        embed.set_footer(text= f"{default.footer()}")
        msg = await ctx.send(embed=embed)
        
        # Reactions
        await msg.add_reaction("🔵")
        await msg.add_reaction("⚪")
        await msg.add_reaction("🟧")
        await msg.add_reaction("❌")

        # Reaction check
        def check(reaction, user):
            return reaction.emoji in ["🔵", "⚪", "🟧", "❌"] and user == ctx.author
        
        # Reaction wait for
        try:
            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=150)
        except asyncio.TimeoutError:
            await msg.delete()
            return

        # Discs
        if reaction.emoji == "🔵":

            # Discs embed
            desc = ""
            for name, value in data['discs'].items():
                desc += f"{value['icon']} {fix(name)}: **Æ**`{value['price']}`\n"
            embed = discord.Embed(title= "Connect 4 - Shop", description= desc, color = 0xFFD700)
            embed.set_footer(text= f"{default.footer()}")
            await msg.delete()
            msg = await ctx.send(embed=embed)

            child = 'discs'

            # Reactions
            await msg.add_reaction("🛒")
            await msg.add_reaction("❌")

            # Reaction check
            def check(reaction, user):
                return reaction.emoji in ["🛒", "❌"] and user == ctx.author
            
            # Reaction wait for
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=150)
            except asyncio.TimeoutError:
                await msg.delete()
                return

            # Buy
            if reaction.emoji == "🛒":
                embed.set_footer(text= f"Choose your purchase.. {default.footer(True)}")
                msg = await msg.edit(embed=embed)

                # Choose item
                while True:
                    
                    # Message check
                    def check(m):
                        fm = unfix(m.content.lower())
                        return fm in data['discs'].keys() or fm in data['backgrounds'].keys() or fm in data['embedColors'].keys() and m.author == ctx.author
                    
                    # Message wait for
                    try:
                        msg = await self.client.wait_for('message', check=check, timeout=150)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return

                    msg = unfix(msg.content.lower())

                    # Discs
                    if msg in data[child].keys() and msg not in invData[child].keys():
                        await db.Update.inventory(ctx.author.id, child, msg)
                        await ctx.send(data[child][msg]['icon'])
                        break
                    
                    else:
                        await ctx.send("Choose a valid item")
            
            # Exit
            if reaction.emoji == "❌": await msg.delete(); return
        
        # Backgrounds
        if reaction.emoji == "⚪":

            # Backgrounds embed
            desc = ""
            for name, value in data['backgrounds'].items():
                desc += f"{value['icon']} {fix(name)}: **Æ**`{value['price']}`\n"
            embed = discord.Embed(title= "Connect 4 - Shop", description= desc, color = 0xFFD700)
            embed.set_footer(text= f"{default.footer()}")
            await msg.delete()
            msg = await ctx.send(embed=embed)

            child = 'backgrounds'

            # Reactions
            await msg.add_reaction("🛒")
            await msg.add_reaction("❌")

            # Reaction check
            def check(reaction, user):
                return reaction.emoji in ["🛒", "❌"] and user == ctx.author
            
            # Reaction wait for
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=150)
            except asyncio.TimeoutError:
                await msg.delete()
                return

            # Buy
            if reaction.emoji == "🛒":
                embed.set_footer(text= f"Choose your purchase.. {default.footer(True)}")
                msg = await msg.edit(embed=embed)

                # Choose item
                while True:

                    # Message check
                    def check(m):
                        fm = unfix(m.content.lower())
                        return fm in data['discs'].keys() or fm in data['backgrounds'].keys() or fm in data['embedColors'].keys() and m.author == ctx.author
                    
                    # Message wait for
                    try:
                        msg = await self.client.wait_for('message', check=check, timeout=150)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return


                    msg = unfix(msg.content.lower())

                    # Discs
                    if msg in data[child].keys() and msg not in invData[child].keys():
                        await db.Update.inventory(ctx.author.id, child, msg)
                        await ctx.send(data[child][msg]['icon'])
                        break
                    
                    else:
                        await ctx.send("Choose a valid item")
            
            # Exit
            if reaction.emoji == "❌": await msg.delete(); return
        
        # Embed colors
        if reaction.emoji == "🟧":

            # Embed colors embed
            desc = ""
            for name, value in data['embedColors'].items():
                desc += f"`{value['icon']}` {fix(name)}: **Æ**`{value['price']}`\n"
            embed = discord.Embed(title= "Connect 4 - Shop", description= desc, color = 0xFFD700)
            embed.set_footer(text= f"{default.footer()}")
            await msg.delete()
            msg = await ctx.send(embed=embed)

            child = 'embedColors'

            # Reactions
            await msg.add_reaction("🛒")
            await msg.add_reaction("❌")

            # Reaction check
            def check(reaction, user):
                return reaction.emoji in ["🛒", "❌"] and user == ctx.author
            
            # Reaction wait for
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=150)
            except asyncio.TimeoutError:
                await msg.delete()
                return

            # Buy
            if reaction.emoji == "🛒":
                embed.set_footer(text= f"Choose your purchase.. {default.footer(True)}")
                msg = await msg.edit(embed=embed)

                # Choose item
                while True:
                    
                    # Message check
                    def check(m):
                        fm = unfix(m.content.lower())
                        return fm in data['discs'].keys() or fm in data['backgrounds'].keys() or fm in data['embedColors'].keys() and m.author == ctx.author
                    
                    # Message wait for
                    try:
                        msg = await self.client.wait_for('message', check=check, timeout=150)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return

                    msg = unfix(msg.content.lower())

                    # Discs
                    if msg in data[child].keys() and msg not in invData[child].keys():
                        await db.Update.inventory(ctx.author.id, child, msg)
                        await ctx.send(data[child][msg]['icon'])
                        break
                    
                    else:
                        await ctx.send("Choose a valid item")
            
            # Exit
            if reaction.emoji == "❌": await msg.delete(); return
        
        # Exit
        if reaction.emoji == "❌": await msg.delete(); return


def setup(client):
    client.add_cog(Handler(client))