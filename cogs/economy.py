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


def setup(client):
    DiscordComponents(client)
    client.add_cog(Economy(client))