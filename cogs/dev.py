import discord, sys, traceback, typing, os, asyncio
from discord.ext import commands
from io import StringIO
from func import database as db
from func.human import *
from func import default


def is_dev(ctx):
    if ctx.author.id in default.developer(): return True
    return False


class Developer(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    @commands.check(is_dev)
    async def reset_games(self, ctx):
        games = db.games; db.games.clear()
        await ctx.send(f"{BOX(PRETTY(games), 'JSON')}\n{BOX(PRETTY(db.games), 'JSON')}")

    @commands.command()
    @commands.check(is_dev)
    async def get_games(self, ctx):
        await ctx.send(BOX(PRETTY(db.games), 'JSON'))
    

    @commands.command()
    @commands.check(is_dev)
    async def get_lobby(self, ctx):
        await ctx.send(BOX(PRETTY(db.Lobby.data), "JSON"))
    
    @commands.command()
    @commands.check(is_dev)
    async def reset_lobby(self, ctx):
        lobby = db.Lobby.data; db.Lobby.data.clear()
        await ctx.send(f"{BOX(PRETTY(lobby), 'JSON')}\n{BOX(PRETTY(db.Lobby.data), 'JSON')}")
    

    @commands.command()
    @commands.check(is_dev)
    async def get_user(self, ctx, user : discord.User):
        user = await db.Get.user(user.id)
        await ctx.send(BOX(PRETTY(user), 'JSON'))


    # Python, Py command
    @commands.command(help="Evaluates Python code.", aliases=['python', 'eval', 'ev'])
    @commands.is_owner()
    async def py(self, ctx, unformatted : typing.Optional[bool], *, cmd):
        await ctx.message.delete()
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        try:
            exec(str(cmd))
        except Exception as e:
            traceback.print_stack(file=sys.stdout)
            print(sys.exc_info())
        sys.stdout = old_stdout
        if (unformatted):
            msg = str(redirected_output.getvalue())
            msg = [await ctx.send(msg[i:i+2000]) for i in range(0, len(msg), 2000)]
        else:
            msg = str(redirected_output.getvalue())
            for i in range(0, len(msg), 2048):
                embed = default.Embed.minimal(None, f"Input:\n{BOX(cmd, 'py')}\nOutput:\n{BOX(msg[i:i+2000], 'cmd')}", "5261F8")
                await ctx.send(embed=embed)


    @commands.command(help="Loads a specific or all cogs.")
    @commands.check(is_dev)
    async def load(self, ctx, cog : typing.Optional[str]):
        if (cog):
            if cog.endswith(".py"):
                cog = cog[:-3]
            try:
                self.client.load_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.author.send(f"[Main]: Failed to load '{cog}': {e}\n")
            else:
                await ctx.send(f"[{cog}]: Loaded..\n", delete_after=5)
        else:
            await ctx.message.add_reaction('✅')

            def check(reaction, user):
                return reaction.emoji == '✅' and ctx.author == user
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=15)
            except asyncio.TimeoutError:
                await ctx.message.delete()

            else:
                for file in os.listdir("cogs"):
                    if file.endswith(".py"):
                        if file[:-3] != "dev":
                            try:
                                self.client.load_extension(f"cogs.{file[:-3]}")
                            except Exception as e:
                                await ctx.author.send(f"[Main]: Failed to load '{file[:-3]}': {e}\n")
                            else:
                                await ctx.send(f"[{file[:-3]}]: Loaded..\n", delete_after=5)

    @commands.command(help="Reloads a specific or all cogs.")
    @commands.check(is_dev)
    async def reload(self, ctx, cog : typing.Optional[str]):
        if (cog):
            if cog.endswith(".py"):
                cog = cog[:-3]
            try:
                self.client.reload_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.author.send(f"[Main]: Failed to reload '{cog}': {e}\n")
            else:
                await ctx.send(f"[{cog}]: Reloaded..\n", delete_after=5)
        else:
            await ctx.message.add_reaction('✅')

            def check(reaction, user):
                return reaction.emoji == '✅' and ctx.author == user
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=15)
            except asyncio.TimeoutError:
                await ctx.message.delete()

            else:
                for file in os.listdir("cogs"):
                    if file.endswith(".py"):
                        try:
                            self.client.reload_extension(f"cogs.{file[:-3]}")
                        except Exception as e:
                            await ctx.author.send(f"[Main]: Failed to reload '{file[:-3]}': {e}\n")
                        else:
                            await ctx.send(f"[{file[:-3]}]: Reloaded..\n", delete_after=5)
    
    @commands.command(help="Unloads a specific or all cogs.")
    @commands.check(is_dev)
    async def unload(self, ctx, cog : typing.Optional[str]):
        if (cog):
            if cog.endswith(".py"):
                cog = cog[:-3]
            if cog == "dev": return
            try:
                self.client.unload_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.author.send(f"[Main]: Failed to unload '{cog}': {e}\n")
            else:
                await ctx.send(f"[{cog}]: Unloaded..\n", delete_after=5)
        else:
            await ctx.message.add_reaction('✅')

            def check(reaction, user):
                return reaction.emoji == '✅' and ctx.author == user
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=15)
            except asyncio.TimeoutError:
                await ctx.message.delete()

            else:
                for file in os.listdir("cogs"):
                    if file.endswith(".py"):
                        if file[:-3] != "dev":
                            try:
                                self.client.unload_extension(f"cogs.{file[:-3]}")
                            except Exception as e:
                                await ctx.author.send(f"[Main]: Failed to unload '{file[:-3]}': {e}\n")
                            else:
                                await ctx.send(f"[{file[:-3]}]: Unloaded..\n", delete_after=5)
    

    @commands.command(help="Updates user's database", aliases=['u'])
    @commands.check(is_dev)
    async def update(self, ctx, member : typing.Optional[discord.User], key : str, value : typing.Union[str, int], overwrite : typing.Optional[bool]):
        user = ctx.author
        if (member):
            user = member
        if (overwrite):
            await db.Update.user(user.id, key, value, overwrite)
            embed = default.Embed.success(None, f"{ctx.author.mention}, Updated {HL(user)} {HL(key)} to {HL(value)}")
            await ctx.send(embed=embed, delete_after=5)
        else:
            await db.Update.user(user.id, key, value, overwrite)
            embed = default.Embed.success(None, f"{ctx.author.mention}, Updated {HL(user)} {HL(key)} by {HL(value)}")
            await ctx.send(embed=embed, delete_after=5)
    
    @commands.command(hidden=True)
    @commands.check(is_dev)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount = 1):
        if amount >= 10:
            embed = default.Embed.minimal(None, f"Are you sure you want to delete {HL(amount)} messages?", "5261f8")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('✅')

            def check(reaction, user):
                return reaction.emoji == '✅' and user == ctx.author
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout = 15)
            except asyncio.TimeoutError:
                await ctx.message.delete()
                await msg.delete()
                return

            else:
                await msg.delete()
                pass

        await ctx.message.delete()
        await ctx.channel.purge(limit=int(amount))
        embed = default.Embed.minimal(None, f"Deleted {HL(amount)} messages in {HL(ctx.guild.name)} ({HL(ctx.channel.name)})", "5261f8")
        await ctx.author.send(embed=embed, delete_after=30)

    
    #! Fix
    @commands.group(hidden=True, invoke_without_command=True, aliases=['bl'], help="Blacklists a server/user from the bot.")
    @commands.check(is_dev)
    async def blacklist(self, ctx, user : discord.Member, remove : typing.Optional[bool] = False):
        await default.Embed.maintenance(ctx); return
        await ctx.send(embed=embed)
    #     if (remove):
    #         await db.Update.blacklist(user.id, True)
    #         await ctx.send(f"Removed {user.mention} from the blacklist")
    #     else:
    #         await db.Update.blacklist(user.id)
    #         print(user.id)
    #         await ctx.send(f"Blacklsited {user.mention}")
    
    @blacklist.command(aliases=['g'])
    @commands.check(is_dev)
    async def guild(self, ctx, guild : discord.Guild, remove : typing.Optional[bool] = False):
        await default.Embed.maintenance(ctx); return
        await ctx.send(embed=embed)
    #     if (remove):
    #         await db.Update.blacklist(guild.id, True)
    #         await ctx.send(f"Removed {HL(guild.name)} from the blacklist")
    #     else:
    #         await db.Update.blacklist(guild.id)
    #         await ctx.send(f"Blacklsited {HL(guild.name)}")


    @commands.command()
    async def dm(self, ctx, member : discord.User, msg, color : typing.Optional[str] = None, title : typing.Optional[str] = None):
        if not (color): await member.send(msg); return
        embed = default.Embed.custom(title, msg, color, None, ctx.author)
        await member.send(embed=embed)
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Developer(client))