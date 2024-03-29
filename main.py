import discord, os, random, typing
from discord.ext import commands, tasks
from func import database as db
from dotenv import load_dotenv
from func import default
from func.human import *

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
        if message.author.id in db.Developers.get(): return "dev."
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

#! Fix
# Blacklist check
# @client.check_once
# def blacklisted(ctx):
#     return str(ctx.author.id) or str(ctx.guild.id) not in db.Get.blacklist()


# Prefix command
@client.command(help="Displays the current prefix and allows you to change it.")
@commands.has_permissions(manage_guild=True)
async def prefix(ctx, new_prefix : typing.Optional[str]):
    if (new_prefix):
        if len(new_prefix) > 3 or len(new_prefix) < 1: await ctx.send(f"Your prefix must be `1`-`3` characters long"); return
        await db.Update.guild(ctx.guild.id, "prefix", new_prefix, True)
        embed = default.Embed.success(None, f"Your prefix has been updated!", None, None, f"New prefix:\s {HL(new_prefix)}")
        await ctx.send(embed=embed, delete_after=30)
    else:
        data = await db.Get.guild(ctx.guild.id)
        embed = default.Embed.minimal(None, f"Current guild prefix: {HL(data['prefix'])}")
        await ctx.send(embed=embed)


# On message event
@client.event
async def on_message(message):
    if (message.author.bot): return


    if client.user.mentioned_in(message):
        prefix = await get_prefix(client, message)
        if not prefix.startswith('<Encrypted>'):
            if not message.content.startswith(str(prefix)):
                embed = default.Embed.minimal(None, f"Current server prefix: {HL(prefix)}")
                await message.channel.send(embed=embed)
            return
        elif message.author.id in db.Developers.get():
            if not message.content.startswith(str(prefix)):
                embed = default.Embed.minimal(None, f"Developer prefix: {HL(prefix)}")
                await message.channel.send(embed=embed)
            return
        else:
            return
    

    users = await db.Fetch.user_ids()
    if str(message.author.id) in users:
        data = await db.Get.user(message.author.id)
        
        if data['exp'] >= int((data['level'] * 4.231) * 100):
            await db.Update.user(message.author.id, 'exp', int(data['exp'] - int((data['level'] * 4.231) * 100)), True)
            await db.Update.user(message.author.id, 'level', 1)
            coinsAmt = random.randint(100,1000)
            await db.Update.user(message.author.id, 'coins', coinsAmt)
            embed = default.Embed.success(None, f"{message.author.mention}, :tada: Congratultations :tada: You've reached level {HL(data['level'] + 1)}!\n:gift: +{HL(coinsAmt)} Coins!")
            await message.channel.send(embed=embed)
            return
        

        # else:

        #     if data['playing'] is True:
        #         if len(db.games) != 0:
        #             for game in db.games:
        #                 if message.author.id in game['players']: break
        #                 else: await db.Update.user(int(message.author.id), "playing", False, True); print("for loop"); break; return
        #         else:
        #             print(len(db.games)); await db.Update.user(int(message.author.id), "playing", False, True); print("length"); return


    await client.process_commands(message)


class Help(commands.HelpCommand):
    def get_command_signature(self, command):
        if (command.signature):
            return f"{HL(self.clean_prefix)}{B(command.qualified_name)} {HL(command.signature)}"
        return f"{HL(self.clean_prefix)}{B(command.qualified_name)}"

    async def send_bot_help(self, mapping):
        embed = default.Embed.minimal("Connect 4 - Help", "<> = Required\n[] = Optional", "5261F8")
        for cog, commands in mapping.items():
            commands = await self.filter_commands(commands)
            command_signatures = [self.get_command_signature(c) for c in commands]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        desc = ""
        commands = await self.filter_commands(cog.get_commands())
        for cmd in commands:
            desc += f"{self.get_command_signature(cmd)}\n"
        embed = default.Embed.minimal(f"Help - {cog.qualified_name}", f"() = Required\n[] = Optional\n\n{B('Commands:')}\n{desc}", "5261F8")
        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_group_help(self, group):
        embed = default.Embed.minimal(f"{group.cog_name} - {group.name}", f"{self.get_command_signature(group)}", "5261F8")
        embed.add_field(name="Description", value=group.help)
        if group.aliases:
            embed.add_field(name="Aliases", value=", ".join(group.aliases), inline=False)
        if group.commands:
            V = ""
            for cmd in group.commands:
                V += f"\n{cmd.qualified_name}".replace(f'{group.name} ', '')
                if (cmd.aliases):
                    V += f" ({HL(', '.join(cmd.aliases))})"
            embed.add_field(name="Subcommands", value=V, inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = default.Embed.minimal(f"{command.cog_name} - {command.name}", f"{self.get_command_signature(command)}", "5261F8")
        embed.add_field(name="Description", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    # async def send_error_message(self, error):
    #     embed = default.Embed.error("CommandNotFound", str(error))
    #     channel = self.get_destination()
    #     await channel.send(embed=embed)

client.help_command = Help()


if __name__ == ('__main__'):
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            try:
                os.listdir('C:\\Users\Marsel')
            except FileNotFoundError:
                try:
                    client.load_extension(f"cogs.{file[:-3]}")
                except Exception as e:
                    print(f"[Main]: Failed to load '{file[:-3]}': {e}\n")
                else:
                    print(f"[{file[:-3]}]: Loaded..\n")
            else:
                if file[:-3] != "events":
                    try:
                        client.load_extension(f"cogs.{file[:-3]}")
                    except Exception as e:
                        print(f"[Main]: Failed to load '{file[:-3]}': {e}\n")
                    else:
                        print(f"[{file[:-3]}]: Loaded..\n")


client.run(os.environ.get("TOKEN"))
