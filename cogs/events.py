import discord, humanize
from discord.ext import commands
from func import default


class Handler(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            T = "CommandOnCooldown"
            D = f"Please wait `{humanize.precisedelta(error.retry_after)}` until next use."

        elif isinstance(error, commands.MissingRequiredArgument):
            T = "MissingRequiredArgument"
            D = f"`{error.param}` is a required argument that is missing."
        
        elif isinstance(error, commands.MemberNotFound):
            T = "MemberNotFound"
            D = f"`{error.argument}` not found"
        
        elif isinstance(error, commands.MissingPermissions):
            T = "MissingPermissions"
            D = f"This command requires the `{error.missing_perms}` permission."
        
        elif isinstance(error, commands.BotMissingPermissions):
            T = "MissingPermissions"
            D = f"`{error.missing_perms}` is a required permission that the bot is missing."
        
        elif isinstance(error, commands.NotOwner):
            T = "NotOwner"
            D = "Only the owner of this bot can run this command."
        
        elif isinstance(error, commands.NSFWChannelRequired):
            T = "NSFWChannelRequired"
            D = "This command only works in `NSFW` channels."
        
        elif isinstance(error, commands.TooManyArguments):
            T = "TooManyArguments"
            D = f"You don't need all these arguments! (`{error.args}`)"
        
        elif isinstance(error, commands.ChannelNotFound):
            T = "ChannelNotFound"
            D = f"`{error.argument}` not found."
        
        elif isinstance(error, commands.ChannelNotReadable):
            T = "ChannelNotReadable"
            D = f"`{error.argument}` is not readable."
        
        else:
            T = "UnknownError"
            D = f"Something went wrong but I can't seem to figure it out. For further assistance visit our [support server](https://discord.gg/JgR6XywMwZ)"
            [await default.Support_server.terminal(self.client, default.Embed.error(T, str(error)[i:i+2000])) for i in range(0, len(str(error)), 2000)]

        embed = default.Embed.error(T, D)
        await ctx.send(embed=embed, delete_after=10)


def setup(client):
    client.add_cog(Handler(client))