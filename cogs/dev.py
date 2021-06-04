import discord, sys, traceback, typing, os, asyncio
from discord.ext import commands
from io import StringIO


class Developer(commands.Cog):
    def __init__(self, client):
        self.client = client


    # Python, Py command
    @commands.command(help="Evaluates Python code.")
    @commands.is_owner()
    async def py(self, ctx, unformatted : typing.Optional[bool] = False, *, cmd):
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
                embed = discord.Embed(title=f"Input:\n```py\n{cmd}\n```", description=f"Output:\n`{msg[i:i+2000]}`", color = 0xF0F0F0)
                await ctx.send(embed=embed)


    @commands.command(help="Loads a specific or all cogs.")
    @commands.is_owner()
    async def load(self, ctx, cog : typing.Optional[str]):
        if (cog):
            if cog.endswith(".py"):
                cog = cog[:-3]
            try:
                self.client.load_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.author.send(f"[Main]: Failed to load '{cog}': {e}\n")
            else:
                await ctx.send(f"[{cog}]: Loaded..\n")
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
                                await ctx.send(f"[{file[:-3]}]: Loaded..\n")

    @commands.command(help="Reloads a specific or all cogs.")
    @commands.is_owner()
    async def reload(self, ctx, cog : typing.Optional[str]):
        if (cog):
            if cog.endswith(".py"):
                cog = cog[:-3]
            try:
                self.client.reload_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.author.send(f"[Main]: Failed to reload '{cog}': {e}\n")
            else:
                await ctx.send(f"[{cog}]: Reloaded..\n")
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
                            await ctx.send(f"[{file[:-3]}]: Reloaded..\n")
    
    @commands.command(help="Unloads a specific or all cogs.")
    @commands.is_owner()
    async def unload(self, ctx, cog : typing.Optional[str]):
        if (cog):
            if cog == "dev" or "dev.py": return
            if cog.endswith(".py"):
                cog = cog[:-3]
            try:
                self.client.unload_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.author.send(f"[Main]: Failed to unload '{cog}': {e}\n")
            else:
                await ctx.send(f"[{cog}]: Unloaded..\n")
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
                                await ctx.send(f"[{file[:-3]}]: Unloaded..\n")


    @commands.command(aliases=['rr'], help="Sends a rickroll GIF in the member's dm.")
    async def rickroll(self, ctx, member : discord.Member):
        embed = discord.Embed(color=0x5261F8)
        embed.set_image(url='https://media.giphy.com/media/Ju7l5y9osyymQ/giphy.gif')
        await member.send(embed=embed)
        await ctx.message.delete()


def setup(client):
    client.add_cog(Developer(client))