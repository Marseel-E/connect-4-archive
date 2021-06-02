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


    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def tech_help(self, ctx):
        embed = discord.Embed(title="Help", description="`-help <category>` for a list of available commands.", color = 0x5261F8)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/827617285899943956/848145731570237470/27304b9b14ce9bd8a28ca637ed92070e-blue-circle-question-mark-icon-by-vexels.png")
        embed.add_field(name=":performing_arts: Fun *(5)*", value="`-help fun`", inline=False)
        embed.add_field(name=":shield: Moderation *(19)*", value="`-help moderation`", inline=False)
        embed.add_field(name=":art: Image *(8)*", value="`-help image`", inline=False)
        embed.add_field(name=":mag: Other *(15)*", value="`-help other`", inline=False)
        embed.add_field(name=":man_technologist: Owner *(?)*", value="`-help owner`", inline=False)
        embed.add_field(name=":eyes: Future *(?)*", value="`-help future`", inline=False)
        embed.set_footer(text= f"Tech © 2021")
        await ctx.send(embed=embed)
    
    @tech_help.command()
    @commands.is_owner()
    async def fun(self, ctx):
        embed = discord.Embed(title="Help - Fun", description="`-help <command>` for detailed information about a specific command.", color = 0x5261F8)
        embed.add_field(name="8ball", value="Answers your question with a 'Yes' or 'No'.\n  __Usage:__ `-8ball <question>`", inline=False)
        embed.add_field(name="flipcoin", value="Flips a coin.\n  __Usage:__ `-flipcoin`", inline=False)
        embed.add_field(name="hbreak", value="Breaks someone's heart.\n  __Usage:__ `-hbreak <@user>`", inline=False)
        embed.add_field(name="math", value="Solves the given equation.\n  __Usage:__ `-math <number> <+ | - | * | / | ^ | //> <number>`", inline=False)
        embed.add_field(name="rolldice", value="Rolls a number between 1 - 6.\n  __Usage:__ `-rolldice`", inline=False)
        embed.set_footer(text= f"Page: 1 - 1 | Tech © 2021")
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Handler(client))