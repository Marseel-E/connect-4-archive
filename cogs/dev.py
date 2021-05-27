import discord, sys, traceback, typing
from discord.ext import commands
from io import StringIO


class Handler(commands.Cog):
    def __init__(self, client):
        self.client = client


    # Python, Py command
    @commands.command(hidden=True)
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


def setup(client):
    client.add_cog(Handler(client))