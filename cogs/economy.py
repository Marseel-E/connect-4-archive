import discord, typing, asyncio
from discord.ext import commands
from func import database as db
from func.human import *
from func import default
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['b', 'bal'], help="Displays your balance.")
    async def balance(self, ctx, member : typing.Optional[discord.Member]):
        user = ctx.author
        if (member):
            user = member
        data = await db.Get.user(user.id)
        embed = discord.Embed(description=f":dollar: Wallet: {data['cash']}\n:credit_card: Bank: {data['bank']}", color = 0xF0F0F0)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text=default.footer())
        msg = await ctx.send(embed=embed, components=[
                Button(style=ButtonStyle.red, label="Deposit"),
                Button(style=ButtonStyle.green, label="Withdraw"),
                ])
        
        def check(res):
            return res.user.id == user.id and res.channel.id == ctx.channel.id

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
        except asyncio.TimeoutError:
            await msg.delete()
            return

        else:
            await res.respond(type=6)
            if res.component.label.lower() == "deposit":
                await msg.delete()
                msg = await ctx.send(f"{user.mention}, How much would you like to deposit? (:dollar: {data['cash']})")
                
                while True:
                    def check(m):
                        return m.author == user
                    
                    try:
                        m = await self.client.wait_for('message', check=check, timeout=30)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        await ctx.send(content=f"{user.mention}, Request timedout.", delete_after=3)
                        break; return
                    
                    else:
                        if int(m.content) <= int(data['cash']) and int(m.content) > 0:
                            amount = int(data['cash']) - int(m.content)
                            await db.Update.user(user.id, "cash", amount, True)
                            await db.Update.user(user.id, "bank", m.content)
                            await msg.delete()
                            await ctx.send(f"{user.mention}, Deposited :dollar: {m.content} to your bank.", delete_after=5)
                            break; return
                        else:
                            continue

            elif res.component.label.lower() == "withdraw":
                await msg.delete()
                msg = await ctx.send(f"{user.mention}, How much would you like to withdraw? (:credit_card: {data['bank']})")
                
                while True:
                    def check(m):
                        return m.author == user
                    
                    try:
                        m = await self.client.wait_for('message', check=check, timeout=30)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        await ctx.send(content=f"{user.mention}, Request timedout.", delete_after=3)
                        break; return
                    
                    else:
                        if int(m.content) <= int(data['bank']) and int(m.content) > 0:
                            amount = int(data['bank']) - int(m.content)
                            await db.Update.user(user.id, "bank", amount, True)
                            await db.Update.user(user.id, "cash", m.content)
                            await msg.delete()
                            await ctx.send(content=f"{user.mention}, Withdrew :dollar: {m.content} from your bank.", delete_after=5)
                            break; return
                        else:
                            continue


    @commands.command(aliases=['s', 'store'], help="Displays Connect 4's shop and allows you to purchase from it.")
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
    DiscordComponents(client)
    client.add_cog(Economy(client))