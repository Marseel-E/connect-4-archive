import discord, typing, asyncio
from discord.ext import commands
from func import database as db
from func.human import *
from func import default


class Handler(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, member : typing.Optional[discord.Member] = None):
        user = ctx.author
        if (member): user = member

        items = await db.Fetch.items()
        data = await db.Get.inventory(user.id)
        
        embed = discord.Embed(title="Connect 4 - Inventory", colour = user.top_role.color)
        
        for child, value in data.items():
            Name = f"**{fix(child)}** `({len(data[child])}/{len(items[child])})`:\n"
            Value = ""
            
            for key, value in value.items():
                if child == "embedColors":
                    Value += f"{fix(key)}: `{value}`\n"
                else:
                    Value += f"{value} {fix(key)}\n"
            embed.add_field(name=Name, value=Value, inline = False)
        embed.set_footer(text= f"{default.footer()}")
        msg = await ctx.send(embed=embed)

        await msg.add_reaction("🤏")

        def check(reaction, u):
            return reaction.emoji == "🤏" and u == user
        
        try:
            reaction, u = await self.client.wait_for('reaction_add', check=check, timeout=300)
        except asyncio.TimeoutError:
            await msg.delete()
            return

        if reaction.emoji == "🤏":
            await ctx.send(f"What would you like to use?")
            def check(m):
                um = unfix(m.content.lower())
                return um in data['discs'].keys() or um in data['backgrounds'].keys() or um in data['embedColors'].keys() and m.author == ctx.author

            try:
                msg = await self.client.wait_for('message', check=check, timeout=150)
            except asyncio.TimeoutError:
                await msg.delete()
                msg = await ctx.send(f"{user.mention}, You didn't respond in time, Request timedout.")
                await asyncio.sleep(5)
                await msg.delete()
                return

            msg = unfix(msg.content.lower())

            while True:

                # Disc
                if msg in data['discs'].keys():
                    await ctx.send(f"Would you like to use that as your `primary` or `secondary` disc?")
                    def check(m):
                        return m.content.lower() in ['primary', 'secondary'] and m.author == ctx.author

                    try:
                        msg2 = await self.client.wait_for('message', check=check, timeout=150)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        msg = await ctx.send(f"{user.mention}, You didn't respond in time, Request timedout.")
                        await asyncio.sleep(5)
                        await msg.delete()
                        break; return

                    await db.Update.user(ctx.author.id, f'{msg2.content.lower()}Disc', data['discs'][msg], True)
                    await ctx.send(f"New {msg2.content.lower()} disc: {data['discs'][msg]}")
                    break
                
                # Background
                elif msg in data['backgrounds'].keys():
                    await db.Update.user(ctx.author.id, 'background', data['backgrounds'][msg], True)
                    await ctx.send(f"New background: {data['backgrounds'][msg]}")
                    break

                # Embed color
                elif msg in data['embedColors'].keys():
                    await db.Update.user(ctx.author.id, 'embedColor', data['embedColors'][msg], True)
                    embed = discord.Embed(description = f"New embed color: `{data['embedColors'][msg]}`", color = int(data['embedColors'][msg], 16))
                    await ctx.send(embed=embed)
                    break
                    
                else:
                    await ctx.send("Choose a valid item!")

        else:
            pass


def setup(client):
    client.add_cog(Handler(client))