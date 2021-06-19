import discord, asyncio, humanize
from discord.ext import commands
from func import default
from func.human import *
from func import database as db
from datetime import datetime, timedelta


class Other(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['bg'], help="Shows how a specific game background would look.")
    async def background(self, ctx, background):
        board = str(str(str(f'{background} ' * 7) + '\n') * 6)
        embed = default.Embed.custom("Connect 4", f"Respond with {HL('1-7')} to play your move.\n{board}", 'F0F0F0', [f":blue_circle: Player 1\s {ctx.author.mention}\s False", f":yellow_circle: Player 2\s {ctx.author}\s False"], None, "ID: 0000000000000000")
        await ctx.send(embed=embed, delete_after=30)


    @commands.command(aliases=['c'], help="Displays how the given color would look as an embed color.")
    async def color(self, ctx, Hex):
        embed = default.Embed.minimal(None, Hex, Hex)
        await ctx.send(embed=embed)
    

    @commands.command(aliases=['rr'], help="Sends a rickroll GIF in the member's dm.")
    @commands.is_owner()
    async def rickroll(self, ctx, member : discord.Member):
        embed = default.Embed.custom(None, None, "5261F8", None, None, None, 'https://media.giphy.com/media/Ju7l5y9osyymQ/giphy.gif')
        await member.send(embed=embed)
        await ctx.message.delete()
    

    @commands.command(help="An advanced embed creation command.\n\n*Use quotations (`' '`) for sentences.\n*Use `None` for an unwanted argument.\n__Example__:\n```\nembed None 'amazing description'\n```That would create an embed with only description.\n\n*Use brackets (`[ ]`) to hold your fields.\n*Field name, value & inline (`True`,`False`) should be seperated by (`\s `) inside your string/quotation, inside the bracket.\n__Example__:\n```\nembed ['field_1\s field_2\s True', 'field_2\s value_2\s True', 'field_3\s value_3\s False']\n```That would create an embed with only 3 fields: if field 1: if 2 will be in the same line but field 3 will be in a seperate line.", aliases=['e'])
    async def embed(self, ctx, title : typing.Optional[str] = None, description : typing.Optional[str] = None, color : typing.Optional[str] = "5261f8", author : typing.Optional[discord.Member] = None, thumbnail : typing.Optional[str] = None, image : typing.Optional[str] = None, footer : typing.Optional[str] = None, fields : typing.Optional[list] = None):
        embed = default.Embed.maintenance()
        await ctx.send(embed=embed)


    @commands.group(invoke_without_command=True, help="Shows the bot's stats.")
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def stats(self, ctx):
        owner = await self.client.fetch_user(470866478720090114)
        users = await db.Fetch.user_ids()
        devs = [i for i in default.developer() if i != 470866478720090114]
        text = ""; games= 0

        for user in users:
            uData = await db.Get.user(user)
            games += (uData['wins'] + uData['draws'] + uData['loses'])

        if (devs):
            for dev in devs:
                dev = await self.client.fetch_user(dev)
                text += f"{dev.mention}\n"
        else:
            text = "None"

        emojis = [f"<:{emoji.name}:{emoji.id}>" for emoji in self.client.emojis]
        
        fields = [
            f"Creator:\s {owner.mention}\s True",
            f"Developer(s):\s {text}\s False",
            f"Guilds:\s {HL(len(self.client.guilds))}\s True",
            f"Users:\s {HL(len(users))}\s True",
            f"Games:\s {HL(games)}\s True",
            f"Commands:\s {HL(len(self.client.commands))}\s False",
            f"Emojis: ({HL(len(self.client.emojis))})\s {''.join(emojis[:30])}\s False",
        ]
        
        embed  = default.Embed.custom("Connect 4 - Stats", self.client.description, "5261f8", fields, None, f"Latency: {round(self.client.latency)}ms", None, self.client.user.avatar_url)
        await ctx.send(embed=embed)
    
    @stats.command(aliases=['g'], help="Shows the guilds the bot is on.")
    @commands.cooldown(1, 600, commands.BucketType.guild)
    async def guilds(self, ctx):
        rs = ['⏮️', '◀️', '⏹️', '▶️', '⏭️']
        pages = []; text = ""; page = 0; total_members = 0
        fives = [i*5 for i in range(len(self.client.guilds))]
        
        for g in self.client.guilds:
            if self.client.guilds.index(g) in fives[1:]:
                pages.append(text)
                text = ""
            else:
                members = g.member_count
                total_members += members
                text += f"{self.client.guilds.index(g)+1}. {g.name} (Members: {HL(members)})\n"
        
        embed = default.Embed.custom(f"Connect 4 - Guilds ({HL(len(self.client.guilds))})", pages[page], "5261f8", None, None, f"Page: {page+1} / {len(pages)} | Users: {total_members}")
        msg = await ctx.send(embed=embed)
        [await msg.add_reaction(r) for r in rs]
        
        while True:
            def check(reaction, user):
                return str(reaction.emoji) in rs and user == ctx.author
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
            except asyncio.TimeoutError:
                await msg.delete()
                break; return
            else:
                if str(reaction.emoji) == '⏮️' and page != 0:
                    page = 0; pass
                elif str(reaction.emoji) == '◀️' and page != 0:
                    page -= 1; pass
                elif str(reaction.emoji) == '⏹️':
                    await msg.delete(); break
                elif str(reaction.emoji) == '▶️' and page != len(pages):
                    page += 1; pass
                elif str(reaction.emoji) == '⏭️' and page != len(pages):
                    page = len(pages); pass
                else:
                    continue
            
            embed = default.Embed.custom(f"Connect 4 - Guilds ({HL(len(self.client.guilds))})", pages[page], "5261f8", None, None, f"Page: {page+1} / {len(pages)} | Users: {total_members}")
            await msg.edit(embed=embed)
            await msg.clear_reactions()
            [await msg.add_reaction(r) for r in rs]
    
    @stats.command(aliases=['u'], help="Shows the people that use the bot and how many games they've played.")
    @commands.cooldown(1, 900, commands.BucketType.guild)
    async def users(self, ctx):
        rs = ['⏮️', '◀️', '⏹️', '▶️', '⏭️']
        users = await db.Fetch.user_ids()
        pages = []; text = ""; page = 0; total_games = 0
        fiftens = [i*15 for i in range(len(users))]

        for u in users:
            if users.index(u) in fiftens[1:]:
                pages.append(text)
                text = ""
            else:
                user = await self.client.fetch_user(int(u))
                uData = await db.Get.user(user.id)
                games = uData['wins'] + uData['draws'] + uData['loses']
                total_games += games
                text += f"{users.index(u)+1}. {user.name} (Games: {HL(games)})\n"

        embed = default.Embed.custom(f"Connect 4 - Users ({HL(len(users))})", pages[page], "5261f8", None, None, f"Page: {page+1} / {len(pages)} | Games: {total_games}")
        msg = await ctx.send(embed=embed)
        [await msg.add_reaction(r) for r in rs]

        while True:
            def check(reaction, user):
                return str(reaction.emoji) in rs and user == ctx.author
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
            except asyncio.TimeoutError:
                await msg.delete()
                break; return
            else:
                if str(reaction.emoji) == '⏮️' and page != 0:
                    page = 0; pass
                elif str(reaction.emoji) == '◀️' and page != 0:
                    page -= 1; pass
                elif str(reaction.emoji) == '⏹️':
                    await msg.delete(); break
                elif str(reaction.emoji) == '▶️' and page != len(pages):
                    page += 1; pass
                elif str(reaction.emoji) == '⏭️' and page != len(pages):
                    page = len(pages); pass
                else:
                    continue

            embed = default.Embed.custom(f"Connect 4 - Users ({HL(len(users))})", pages[page], "5261f8", None, None, f"Page: {page+1} / {len(pages)} | Games: {total_games}")
            await msg.edit(embed=embed)
            await msg.clear_reactions()
            [await msg.add_reaction(r) for r in rs]
    

    @commands.command(aliases=['bug', 'report', 'br'], help="Report a bug/error in the bot.")
    async def bug_report(self, ctx, *, description : str):
        embed = default.Embed.custom("Bug report", description, default.Color.red, None, None, f"ID: {ctx.author.id}")
        channel = await self.client.fetch_channel(855139711554289674)
        await channel.send(embed=embed)
    

    @commands.command(aliases=['perms'], help="Shows the permissions the bot requires and their current status.")
    @commands.has_permissions(manage_roles=True)
    async def permissions(self, ctx):
        required = ""
        optional = ""
        other = ""

        rPerms = ["add_reactions", "embed_links", "external_emojis", "read_messages", "use_external_emojis", "view_channel", "send_messages"]
        oPerms = ["attach_files", "change_nickname", "create_instant_invite", "manage_messages", "read_message_history"]
        perms = list(ctx.guild.me.guild_permissions)

        for perm in perms:
            if (perm[1]):
                if perm[0] in rPerms:
                    required += f"{HL(perm[0])}\n"
                elif perm[0] in oPerms:
                    optional += f"{HL(perm[0])}\n"
                else:
                    other += f"{HL(perm[0])}\n"
            else:
                if perm[0] in rPerms:
                    required += f":warning: {HL(perm[0])} {I('(Missing)')}\n"
                elif perm[0] in oPerms:
                    optional += f":warning: {HL(perm[0])} {I('(Missing)')}\n"
                else:
                    pass

        fields = [f":white_check_mark: Required:\s {required}\s False", f":ballot_box_with_check: Optional:\s {optional}\s False"]
        if other != "":
            fields.append(f":no_entry_sign: Not required:\s {other}\s False")

        embed = default.Embed.custom("Connect 4 - Permissions", None, default.Color.blurple, fields)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Other(client))