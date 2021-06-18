import discord, asyncio
from discord.ext import commands
from func import default
from func.human import *


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
    

    @commands.command(hidden=True, help="An advanced embed creation command.\n\n*Use quotations (`' '`) for sentences.\n*Use `None` for an unwanted argument.\n__Example__:\n```\nembed None 'amazing description'\n```That would create an embed with only description.\n\n*Use brackets (`[ ]`) to hold your fields.\n*Field name, value & inline (`True`,`False`) should be seperated by (`\s `) inside your string/quotation, inside the bracket.\n__Example__:\n```\nembed ['field_1\s field_2\s True', 'field_2\s value_2\s True', 'field_3\s value_3\s False']\n```That would create an embed with only 3 fields: if field 1: if 2 will be in the same line but field 3 will be in a seperate line.", aliases=['e'])
    async def embed(self, ctx, title : typing.Optional[str] = None, description : typing.Optional[str] = None, color : typing.Optional[str] = "5261f8", author : typing.Optional[discord.Member] = None, thumbnail : typing.Optional[str] = None, image : typing.Optional[str] = None, footer : typing.Optional[str] = None, fields : typing.Optional[list] = None):
        embed = default.Embed.maintenance()
        await ctx.send(embed=embed)


    @commands.group(invoke_without_command=True, help="Shows the bot's stats.")
    async def stats(self, ctx):
        owner = await self.client.fetch_user(470866478720090114)
        devs = ""
        for i in default.developer():
            if i == 470866478720090114: pass
            else:
                dev = await self.client.fetch_user(i)
                devs += f"{dev.mention}\n"
        emojis = [f"<:{emoji.name}:{emoji.id}>" for emoji in self.client.emojis]
        fields = [
            f"Creator:\s {owner.mention}\s True",
            f"Developers:\s {devs}\s False",
            f"Guilds:\s {HL(len(self.client.guilds))}\s True",
            f"Users:\s {HL(len([i for i in self.client.users if not (i.bot)]))}\s True",
            f"Commands:\s {HL(len(self.client.commands))}\s False",
            f"Emojis: ({HL(len(self.client.emojis))})\s {''.join(emojis[:30])}\s False",
        ]
        embed  = default.Embed.custom("Connect 4 - Stats", self.client.description, "5261f8", fields, None, f"Latency: {round(self.client.latency)}ms", None, self.client.user.avatar_url)
        await ctx.send(embed=embed)
    
    @stats.command(aliases=['g'], help="Shows the guilds the bot is on.")
    @commands.is_owner()
    async def guilds(self, ctx):
        pages = []
        text = ""
        page = 0
        fives = [i*5 for i in range(len(self.client.guilds))]
        i = 0
        while i in range(len(self.client.guilds)):
            for guild in self.client.guilds:
                i += 1
                if i-1 in fives[1:]:
                    pages.append(text)
                    text = ""
                else:
                    text += f"{i}. {guild.name} ({HL(guild.member_count)})\n"
        while True:
            embed = default.Embed.custom(f"Connect 4 - Guilds ({HL(len(self.client.guilds))})", pages[page], "5261f8", None, None, f"Page: {page+1} / {len(pages)}")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('⬅️')
            await msg.add_reaction('➡️')

            while True:
                def check(reaction, user):
                    return str(reaction.emoji) in ['⬅️', '➡️'] and user == ctx.author
                
                try:
                    reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=30)
                except asyncio.TimeoutError:
                    await msg.delete()
                    break; break; return
                else:
                    if str(reaction.emoji) == '⬅️' and page != 0:
                        page -= 1; break
                    if str(reaction.emoji) == '➡️' and page+1 != len(pages):
                        page += 1; break
    

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