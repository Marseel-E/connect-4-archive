import discord, typing, asyncio, random, humanize
from discord.ext import commands
from func import database as db
from func.human import *
from func import default
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(alises=['r', 'steal'], help="Steal :dollar:money from someone.", hidden=True)
    @commands.cooldown(1, 160)
    async def rob(self, ctx, member : discord.Member):
        mData = await db.Get.user(member.id)
        if mData['cash'] <= 1000: embed = default.Embed.error(None, f"{ctx.author.mention}, {member} is too poor to rob."); await ctx.send(embed=embed, delete_after=5)
        amount = random.randint(1001, int(mData['cash']))
        await db.Update.user(ctx.author.id, 'cash', amount)
        await db.Update.user(member.id, 'cash', int(mData['cash']) - amount, True)
        embed = default.Embed.success(None, f"{ctx.author.mention}, You've stolen :dollar: {amount} from {member}")
        await ctx.send(embed=embed, delete_after=30)


    @commands.command(aliases=['b', 'bal'], help="Displays your balance.", hidden=True)
    async def balance(self, ctx, member : typing.Optional[discord.Member]):
        user = ctx.author
        if (member):
            user = member
        data = await db.Get.user(user.id)
        embed = default.Embed.custom(None, f":dollar: Wallet: {data['cash']}\n:credit_card: Bank: {data['bank']}", "5261f8", None, user)
        msg = await ctx.send(embed=embed, components=[
                [Button(style=ButtonStyle.red, label="Deposit"),
                Button(style=ButtonStyle.green, label="Withdraw")],
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
                embed = default.Embed.minimal(None, f"{user.mention}, How much would you like to deposit? (:dollar: {data['cash']})")
                msg = await ctx.send(embed=embed)
                
                while True:
                    def check(m):
                        return m.author == user
                    
                    try:
                        m = await self.client.wait_for('message', check=check, timeout=30)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        break; return
                    
                    else:
                        if int(m.content) <= int(data['cash']) and int(m.content) > 0:
                            amount = int(data['cash']) - int(m.content)
                            await db.Update.user(user.id, "cash", amount, True)
                            await db.Update.user(user.id, "bank", m.content)
                            await msg.delete()
                            embed = default.Embed.success(None, f"{user.mention}, Deposited :dollar: {m.content} to your bank.")
                            await ctx.send(embed=embed, delete_after=5)
                            break; return
                        else:
                            continue

            elif res.component.label.lower() == "withdraw":
                await msg.delete()
                embed = default.Embed.minimal(None, f"{user.mention}, How much would you like to withdraw? (:credit_card: {data['bank']})")
                msg = await ctx.send(embed=embed)
                
                while True:
                    def check(m):
                        return m.author == user
                    
                    try:
                        m = await self.client.wait_for('message', check=check, timeout=30)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        break; return
                    
                    else:
                        if int(m.content) <= int(data['bank']) and int(m.content) > 0:
                            amount = int(data['bank']) - int(m.content)
                            await db.Update.user(user.id, "bank", amount, True)
                            await db.Update.user(user.id, "cash", m.content)
                            await msg.delete()
                            embed = default.Embed.success(None, f"{user.mention}, Withdrew :dollar: {m.content} from your bank.")
                            await ctx.send(embed=embed, delete_after=5)
                            break; return
                        else:
                            continue


    @commands.command(aliases=['s', 'store'], help="Displays Connect 4's shop and allows you to purchase from it.")
    async def shop(self, ctx, category : typing.Optional[str] = None):
        # Data
        data = await db.Fetch.items()
        invData = await db.Get.inventory(ctx.author.id)
        userData = await db.Get.user(ctx.author.id)
        
        # Direct category
        if (category): pass
        
        # Main embed
        embed = default.Embed.minimal("Connect 4 - Shop", ":blue_circle: Discs \n:white_circle: Backgrounds \n:orange_square: Embed colors")
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
            embed = default.Embed.minimal("Connect 4 - Shop", desc)
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
                        if userData['coins'] >= data[child][msg]['price']:
                            await db.Update.user(ctx.author.id, 'coins', int(userData['coins'] - data[child][msg]['price']), True)
                            await db.Update.inventory(ctx.author.id, child, msg)
                            embed = default.Embed.success(None, f"{ctx.author.mention}, You purchased {data[child][msg]['icon']} for Æ`{data[child][msg]['price']}`")
                            await ctx.send(embed=embed, delete_after=5)
                            break
                        else:
                            embed = default.Embed.error(None, f"You don't have Æ`{data[child][msg]['price']}`")
                            await ctx.send(embed=embed, delete_after=5)
                    
                    else:
                        embed = default.Embed.minimal(None, "Choose a valid item")
                        await ctx.send(embed=embed, delete_after=5)
            
            # Exit
            if reaction.emoji == "❌": await msg.delete(); return
        
        # Backgrounds
        if reaction.emoji == "⚪":

            # Backgrounds embed
            desc = ""
            for name, value in data['backgrounds'].items():
                desc += f"{value['icon']} {fix(name)}: **Æ**`{value['price']}`\n"
            embed = default.Embed.minimal("Connect 4 - Shop", desc)
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
                        if userData['coins'] >= data[child][msg]['price']:
                            await db.Update.user(ctx.author.id, 'coins', int(userData['coins'] - data[child][msg]['price']), True)
                            await db.Update.inventory(ctx.author.id, child, msg)
                            embed = default.Embed.success(None, f"{ctx.author.mention}, You purchased {data[child][msg]['icon']} for Æ`{data[child][msg]['price']}`")
                            await ctx.send(embed=embed, delete_after=5)
                            break
                        else:
                            embed = default.Embed.error(None, f"You don't have Æ`{data[child][msg]['price']}`")
                            await ctx.send(embed=embed, delete_after=5)
                    
                    else:
                        embed = default.Embed.minimal(None, "Choose a valid item")
                        await ctx.send(embed=embed, delete_after=5)
            
            # Exit
            if reaction.emoji == "❌": await msg.delete(); return
        
        # Embed colors
        if reaction.emoji == "🟧":

            # Embed colors embed
            desc = ""
            for name, value in data['embedColors'].items():
                desc += f"`{value['icon']}` {fix(name)}: **Æ**`{value['price']}`\n"
            embed = default.Embed.minimal("Connect 4 - Shop", desc)
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
                        if userData['coins'] >= data[child][msg]['price']:
                            await db.Update.user(ctx.author.id, 'coins', int(userData['coins'] - data[child][msg]['price']), True)
                            await db.Update.inventory(ctx.author.id, child, msg)
                            embed = default.Embed.success(None, f"{ctx.author.mention}, You purchased {data[child][msg]['icon']} for Æ`{data[child][msg]['price']}`")
                            await ctx.send(embed=embed, delete_after=5)
                            break
                        else:
                            embed = default.Embed.error(None, f"You don't have Æ`{data[child][msg]['price']}`")
                            await ctx.send(embed=embed, delete_after=5)
                    
                    else:
                        embed = default.Embed.minimal(None, "Choose a valid item")
                        await ctx.send(embed=embed, delete_after=5)
            
            # Exit
            if reaction.emoji == "❌": await msg.delete(); return
        
        # Exit
        if reaction.emoji == "❌": await msg.delete(); return


def setup(client):
    DiscordComponents(client)
    client.add_cog(Economy(client))