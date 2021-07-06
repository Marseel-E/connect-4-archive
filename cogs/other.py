import discord, asyncio, humanize
from discord.ext import commands
from func import default
from func.human import *
from func import database as db
from datetime import datetime, timedelta
from func.default import limit


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
    

    @commands.command(help="Advanced embed creation command.", aliases=['create-embed', 'e'])
    async def embed(self, ctx):
        TITLE = None; DESCRIPTION = None; COLOR = '000000'; AUTHOR = None; FOOTER = None; IMAGE = None; THUMBNAIL = None; FIELDS = None
        
        tmt = 120

        async def TIMEOUT():
            await message.delete()
            embed = default.Embed.error('MessageTimedOut', f"{ctx.author.mention}, You failed to respond in-time.")
            await ctx.send(embed=embed, delete_after=15)
        
        async def LIMIT(limit : int):
            await message.delete()
            embed = default.Embed.error('LimitReached', f"You've reached the maximum character limit. ([{len(message.content)}]({message.jump_url})/{HL(limit)})")
            await ctx.send(embed=embed, delete_after=15)
        
        async def LINK():
            await message.delete()
            embed = default.Embed.error('ValueError', f"This value should be a link type. \n({HL('https://imgur.com/gallery/q261Q')})")
            await ctx.send(embed=embed, delete_after=15)
        
        def RULE(limit : typing.Optional[int] = None):
            text = f"Respond with {HL('no')} if you don't want this value."
            if (limit): text = f"Respond with {HL('no')} if you don't want this value.\n (Limit: {HL(limit)})"
            return text
        
        embed = default.Embed.minimal("RULES", f"-Embed sum must not exceed 6000!\n-Each embed value has its own limit!\n-Respond with a {HL('no')} if you don't want a specific value.", default.Color.blurple)
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3.0)

        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        # Title, Description, Color

        #- Title
        embed = default.Embed.minimal(f"What would you like your {HL('title')} to be ?", RULE(limit['title']), default.Color.dark_grey)
        await msg.edit(embed=embed)

        while True:
            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                else:
                    if len(message.content) > limit['title']: await LIMIT(limit['title']); continue
                    TITLE = message.content; await message.delete(); break

        #- Description
        embed = default.Embed.minimal(None, f"What would you like your {HL('description')} to be ?\n{RULE(limit['description'])}", default.Color.dark_grey)
        await msg.edit(embed=embed)

        while True:
            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                else:
                    if len(message.content) > limit['description']: await LIMIT(limit['description']); continue
                    DESCRIPTION = message.content; await message.delete(); break

        #- Color
        embed = default.Embed.minimal(f"What would you like your {HL('color')} to be ?", f"{HL(default.Color.blurple)}\n{RULE()}", default.Color.blurple)
        await msg.edit(embed=embed)

        while True:
            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                if int(message.content, 16) > 16777215: await message.delete(); await ctx.send("Please use a valid HEX color code"); continue
                else: COLOR = message.content; await message.delete(); break

        # Author, Footer

        #- Author
        embed = default.Embed.custom(f"Who would you like your {HL('author')} to be ?", RULE(limit['author']), default.Color.dark_grey, None, ctx.author)
        await msg.edit(embed=embed)

        while True:
            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                else:
                    if len(message.content) > limit['author']: await LIMIT(limit['author']); continue
                    AUTHOR = message.mentions[0]; await message.delete(); break
        
        #- Footer
        embed = default.Embed.custom(None, RULE(limit['footer']), default.Color.dark_grey, None, None, f"What would you like your footer to be ?")
        await msg.edit(embed=embed)

        while True:
            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                else:
                    if len(message.content) > limit['footer']: await LIMIT(limit['footer']); continue
                    FOOTER = message.content; await message.delete(); break

        # Image, Thumbnail
        
        #- Image
        embed = default.Embed.custom(f"What would you like your image to be ?", RULE(), default.Color.dark_grey, None, None, None, 'https://imgur.com/gallery/q261Q')
        await msg.edit(embed=embed)

        while True:
            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                else:
                    if not message.content.startswith('https://'): await LINK(); continue
                    IMAGE = message.content; await message.delete(); break
        
        #- Thumbnail
        embed = default.Embed.custom(f"What would you like the thumbnail to be ?", RULE(), default.Color.dark_grey, None, None, None, None, 'https://imgur.com/gallery/q261Q')
        await msg.edit(embed=embed)

        while True:
            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                else:
                    if not message.content.startswith('https://'): await LINK(); continue
                    THUMBNAIL = message.content; await message.delete(); break

        # Fields
        while True:
            embed = default.Embed.custom(None, None, default.Color.dark_grey, ['Would you like to\s add a field ?\s True'], None, "Yes / No")
            await msg.edit(embed=embed)

            try: message = await self.client.wait_for('message', check=check, timeout=tmt)
            except asyncio.TimeoutError: await TIMEOUT(); break
            else:
                if message.content.lower() == "no": await message.delete(); break
                if message.content.lower() == "yes":
                    if FIELDS == None: FIELDS = []
                    await message.delete()

                    embed = default.Embed.custom(f"What would you like the {HL('name')} to be?", None, default.Color.dark_grey, ['Name\s Value\s True'])
                    await msg.edit(embed=embed)
                    
                    while True:
                        try: message = await self.client.wait_for('message', check=check, timeout=tmt)
                        except asyncio.TimeoutError: await TIMEOUT(); break
                        else:
                            if len(message.content) > limit['field']['name']: await LIMIT(limit['field']['name']); continue
                            FIELD_NAME = message.content; await message.delete(); break
                    
                    embed = default.Embed.custom(f"What would you like the {HL('value')} to be?", None, default.Color.dark_grey, ['Name\s Value\s True'])
                    await msg.edit(embed=embed)
                    
                    while True:
                        try: message = await self.client.wait_for('message', check=check, timeout=tmt)
                        except asyncio.TimeoutError: await TIMEOUT(); break
                        else:
                            if len(message.content) > limit['field']['value']: await LIMIT(limit['field']['value']); continue
                            FIELD_VALUE = message.content; await message.delete(); break
                    
                    embed = default.Embed.custom(f"Would you like the field to be {HL('inline')} with the previous/next field?", None, default.Color.dark_grey, None, None, "Yes/No")
                    await msg.edit(embed=embed)
                    
                    while True:
                        try: message = await self.client.wait_for('message', check=check, timeout=tmt)
                        except asyncio.TimeoutError: await TIMEOUT(); break
                        else:
                            if message.content.lower() == "no": FIELD_INLINE = False; await message.delete(); break
                            if message.content.lower() == "yes": FIELD_INLINE = True; await message.delete(); break
                
                FIELDS.append(f"{FIELD_NAME}\s {FIELD_VALUE}\s {FIELD_INLINE}")

        embed = default.Embed.success(None, "Preparing embed...")
        await msg.edit(embed=embed)

        # Send
        embed = default.Embed.custom(TITLE, DESCRIPTION, COLOR, FIELDS, AUTHOR, FOOTER, IMAGE, THUMBNAIL)
        await msg.delete(); await ctx.send(embed=embed)


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
        rs = ['◀️', '⏹️', '▶️']
        pages = []; text = ""; page = 0; total_members = 0
        tens = [i*10 for i in range(len(self.client.guilds))]
        
        for g in self.client.guilds:
            if self.client.guilds.index(g)+1 in tens[1:]:
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
                if str(reaction.emoji) == '◀️' and page > 0:
                    page -= 1; pass
                elif str(reaction.emoji) == '⏹️':
                    await msg.delete(); break
                elif  str(reaction.emoji) == '▶️' and page+1 < len(pages): 
                    page += 1; pass
                else:
                    continue
            
            embed = default.Embed.custom(f"Connect 4 - Guilds ({HL(len(self.client.guilds))})", pages[page], "5261f8", None, None, f"Page: {page+1} / {len(pages)} | Users: {total_members}")
            await msg.edit(embed=embed)
            await msg.clear_reactions()
            [await msg.add_reaction(r) for r in rs]
    
    @stats.command(aliases=['u'], help="Shows the people that use the bot and how many games they've played.")
    @commands.cooldown(1, 900, commands.BucketType.guild)
    async def users(self, ctx):
        rs = ['◀️', '⏹️', '▶️']
        users = await db.Fetch.user_ids()
        pages = []; text = ""; page = 0; total_games = 0
        fiftens = [i*15 for i in range(len(users))]

        for u in users:
            if users.index(u)+1 in fiftens[1:]:
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
                if str(reaction.emoji) == '◀️' and page > 0:
                    page -= 1
                elif str(reaction.emoji) == '⏹️':
                    await msg.delete(); break
                elif str(reaction.emoji) == '▶️' and page+1 < len(pages):
                    page += 1
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
        embed = default.Embed.success(None, f"Thanks for reaching out, Your report has been sent.\nPlease be patient while waiting for a response from our support team.\nVisit our {B(default.support_server)} for urgent help.")
        await ctx.send(embed=embed)
    

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
    

    @commands.command(aliases=['links', 'l', 'link', 'bot_invite', 'bot', 'bot_link'], help="Displays the Bot & Support Server invite links")
    async def invite(self, ctx):
        embed = default.Embed.minimal("Connect 4 - Links", f"{B(default.bot)}\n{B(default.support_server)}", default.Color.blurple)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Other(client))