import discord, os, random, asyncio, humanize, typing
from discord.ext import commands
from func import database as db
from dotenv import load_dotenv
from datetime import datetime, timedelta
from func import default

load_dotenv('func\.env')

# Prefix
async def get_prefix(bot, message):
    if (message.author.bot): return
    data = await db.Get.guild(message.guild.id)
    try:
        os.listdir('C:\\Users\Marsel')
    except FileNotFoundError:
        return data['prefix']
    else:
        if message.author.id == default.developer(): return "dev."
        return "<Encrypted>" + str(random.randint(1000000000,9999999999))

# Intents
intents = discord.Intents.default()
intents.guilds=True
intents.members=True
intents.reactions=True
intents.voice_states=True

# Client
client = commands.Bot(command_prefix=get_prefix, case_sensitive=True, intents=intents)


# On ready event
@client.event
async def on_ready():
    print("running...")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f"connect-4.exe"))


# Prefix command
@client.command(help="Displays the current prefix and allows you to change it.")
@commands.has_permissions(manage_guild=True)
async def prefix(ctx, new_prefix : typing.Optional[str]):
    if (new_prefix):
        if len(new_prefix) > 3 or len(new_prefix) < 1: await ctx.send(f"Your prefix must be `1`-`3` characters long"); return
        await db.Update.guild(ctx.guild.id, "prefix", new_prefix, True)
        await ctx.send(f"Your prefix has been updated!\nNew prefix: `{new_prefix}`")
    else:
        data = db.Get.guild(ctx.guild.id)
        await ctx.send(f"Current guild prefix: `{data['prefix']}`")
    

# Prefix error handler
@prefix.error
async def prefix_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, This command requires the "`Manage Server`" permission.')
    else: await ctx.send(f"{ctx.author.mention}, Something went wrong but I can't seem to figure it out. For further assistance visit our [support server](https://discord.gg/WZw6BV5YCP)")


# On message event
@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        prefix = await get_prefix(client, message)
        if not message.content.startswith(str(prefix)): await message.channel.send(f"Current server prefix: `{prefix}`")
        return
    
    await client.process_commands(message)


@client.command(aliases=['c'], help="Displays how the given color would look as an embed color.")
async def color(ctx, hex):
    embed = discord.Embed(description = hex, color= int(str(hex), 16))
    embed.set_footer(default.footer())
    await ctx.send(embed=embed)


class Help(commands.HelpCommand):
    def get_command_signature(self, command):
        return f"`{self.clean_prefix}`{command.qualified_name} `{command.signature}`"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Connect 4 - Help", color=0x5261F8)
        for cog, commands in mapping.items():
            commands = await self.filter_commands(commands)
            command_signatures = [self.get_command_signature(c) for c in commands]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_command_help(self, command):
        embed = discord.Embed(title=f"{command.cog_name} - {command.name}", description=self.get_command_signature(command), color=0x5261F8)
        embed.add_field(name="Description", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_cog_help(self, cog):
        desc = ""
        commands = await self.filter_commands(cog.get_commands())
        for cmd in commands:
            desc += f"{self.get_command_signature(cmd)}\n"
        embed = discord.Embed(title=f"Help - {cog.qualified_name}", description=desc, color=0x5261F8)
        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_group_help(self, group):
        embed = discord.Embed(title=f"{group.cog_name} - {group.name}", description=self.get_command_signature(group), color=0x5261F8)
        embed.add_field(name="Description", value=group.help)
        alias = group.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=str(error), color=0x5261F8)
        channel = self.get_destination()
        await channel.send(embed=embed)

client.help_command = Help()


if __name__ == ('__main__'):
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            try:
                client.load_extension(f"cogs.{file[:-3]}")
            except Exception as e:
                print(f"[Main]: Failed to load '{file[:-3]}': {e}\n")
            else:
                print(f"[{file[:-3]}]: Loaded..\n")

client.run(os.environ.get("TOKEN"))
