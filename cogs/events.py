import discord, humanize
from discord.ext import commands
from func import default
from func import database as db


def is_not_dev(ctx):
    if ctx.author.id not in default.developer(): return True
    return False

class Handler(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            T = "CommandOnCooldown"
            D = f"Please wait `{humanize.precisedelta(error.retry_after)}` until next use."

        if isinstance(error, commands.MissingRequiredArgument):
            T = "MissingRequiredArgument"
            D = f"`{error.param}` is a required argument that is missing."
        
        if isinstance(error, commands.MemberNotFound):
            T = "MemberNotFound"
            D = f"`{error.argument}` not found"
        
        if isinstance(error, commands.MissingPermissions):
            T = "MissingPermissions"
            D = f"This command requires the `{error.missing_perms}` permission."
        
        if isinstance(error, commands.BotMissingPermissions):
            T = "MissingPermissions"
            D = f"`{error.missing_perms}` is a required permission that the bot is missing."
        
        if isinstance(error, commands.NotOwner):
            T = "NotOwner"
            D = "Only the owner of this bot can run this command."
        
        if isinstance(error, commands.NSFWChannelRequired):
            T = "NSFWChannelRequired"
            D = "This command only works in `NSFW` channels."
        
        if isinstance(error, commands.TooManyArguments):
            T = "TooManyArguments"
            D = f"You don't need all these arguments! (`{error.args}`)"
        
        if isinstance(error, commands.ChannelNotFound):
            T = "ChannelNotFound"
            D = f"`{error.argument}` not found."
        
        if isinstance(error, commands.ChannelNotReadable):
            T = "ChannelNotReadable"
            D = f"`{error.argument}` is not readable."
        
        else:
            print(error)
            return

        embed = discord.Embed(title=T, description=D, color=0xFF0000)
        embed.set_footer(text=default.footer())
        await ctx.send(embed=embed, delete_after=10)


def setup(client):
    client.add_cog(Handler(client))