import discord, asyncio, humanize, typing, random
from discord.ext import commands
from func import database as db
from func import default
from datetime import datetime, timedelta
from func.human import *


class Backend:

    # Game play move
    async def playMove(gameId, col):
        game = await db.Get.game(gameId)
        board = game['board']
        player = (game['players'].index(game['turn']) + 1)
        for row in reversed(range(len(board))):
            if row == 0 and board[row][int(col)] != '0':
                return False 
            
            if board[row][int(col)] == '0':
                board[row][int(col)] = str(player)
                await db.Update.game(gameId, "board", board, True)
                return True

    # Game wich check
    async def winCheck(gameId):
        game = await db.Get.game(gameId)
        board = game['board']
        player = (game['players'].index(game['turn']) + 1)
        columns = 7
        rows = 6

        # Horizontal
        for col in range(columns-3):
            for row in range(rows):
                if board[row][col] == str(player) and board[row][col+1] == str(player) and board[row][col+2] == str(player) and board[row][col+3] == str(player):
                    board[row][col] = 'h'
                    board[row][col+1] = 'h'
                    board[row][col+2] = 'h'
                    board[row][col+3] = 'h'
                    return True

        # Vertical
        for col in range(columns):
            for row in range(rows-3):
                if board[row][col] == str(player) and board[row+1][col] == str(player) and board[row+2][col] == str(player) and board[row+3][col] == str(player):
                    board[row][col] = 'v'
                    board[row+1][col] = 'v'
                    board[row+2][col] = 'v'
                    board[row+3][col] = 'v'
                    return True

        # Ascend
        for col in range(columns-3):
            for row in range(rows-3):
                if board[row][col] == str(player) and board[row+1][col+1] == str(player) and board[row+2][col+2] == str(player) and board[row+3][col+3] == str(player): 
                    board[row][col] = 'a'
                    board[row+1][col+1] = 'a'
                    board[row+2][col+2] = 'a'
                    board[row+3][col+3] = 'a'
                    return True

        # Descend
        for col in range(columns-3):
            for row in range(3,rows):
                if board[row][col] == str(player) and board[row-1][col+1] == str(player) and board[row-2][col+2] == str(player) and board[row-3][col+3] == str(player):
                    board[row][col] = 'd'
                    board[row-1][col+1] = 'd'
                    board[row-2][col+2] = 'd'
                    board[row-3][col+3] = 'd'
                    return True
        
        return False

    # Game draw check
    async def drawCheck(gameId):
        game = await db.Get.game(gameId)
        board = game['board']
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] == '0': return False            
        return True

    # Game board formatter
    async def prettierGame(gameId):
        game = await db.Get.game(gameId)
        user = await db.Get.user(game['players'][0])
        theme = await db.Get.theme(game)
        board = game['board']; newBoard = ""
        for row in range(len(board)):
            newBoard += f"\n"
            for col in range(len(board[row])):
                if board[row][col] == '0': newBoard += f"{theme['background']} "
                if board[row][col] == '1': newBoard += f"{theme['oneDisc']} "
                if board[row][col] == '2': newBoard += f"{theme['twoDisc']} "
                if board[row][col] == 'v': newBoard += "<:c4_vertical:855634500963926036> "
                if board[row][col] == 'h': newBoard += "<:c4_horizontal:855634968750325791> "
                if board[row][col] == 'a': newBoard += "<:c4_ascending:855634992159522886> "
                if board[row][col] == 'd': newBoard += "<:c4_descending:855635141057576971> "
        return newBoard
    
    # Fetch game
    async def fetchGame(userId):
        games = await db.Fetch.game_ids()
        for id in games:
            gData = await db.Get.game(id)
            if userId in gData['players']:
                return gData


class Game(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(help="Displays the game board.")
    async def board(self, ctx):
        uData = await db.Get.user(ctx.author.id)

        if not (uData['playing']): await ctx.send(f"{ctx.author.mention}, Your not playing.", delete_after=5); return
        
        gData = await Backend.fetchGame(ctx.author.id)
        board = await Backend.prettierGame(gData['id'])
        theme = await db.Get.theme(gData)

        member = await self.client.fetch_user(gData['players'][1])

        embed = discord.Embed(title=f"**{ctx.author.name} <:vs_1:851712364826853376> {member.name}**", description=f"Reply with `1`-`7` to place your move.\n{board}", color = int(theme['embedColor'], 16))
        
        if gData['turn'] == ctx.author.id:
            embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author.mention} *`(Your turn!)`*", inline=False)
            embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member}", inline=False)
        else:
            embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author}", inline=False)
            embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member.mention} *`(Your turn!)`*", inline=False)
        
        embed.set_footer(text=f"ID: {gData['id']} {default.footer(True)}")
        await ctx.send(embed=embed)


    # Play command
    @commands.group(invoke_without_command=True, help="Play a game of Connect 4 against someone.")
    async def play(self, ctx, member : discord.Member):
        # Checks
        if (member.bot): return
        if member == ctx.author: await ctx.send("No. Just.. No, NO!"); return
        playerOne = await db.Get.user(ctx.author.id)
        playerTwo = await db.Get.user(member.id)
        if (playerOne['playing']): await ctx.send(f"You're already playing a game!"); return
        if (playerTwo['playing']): await ctx.send(f"Your opponent is playing a game already!"); return

        # Opponent
        msg = await ctx.send(f"{member.mention}, {ctx.author} invited you to a Connect 4 game would you like to play?")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == member and str(reaction.emoji) in ["✅", "❌"]
        try:
            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=150.0)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"{ctx.author.mention}, {member} didn't respond in time. Request timedout!", delete_after=5)
            return
        
        if reaction.emoji == "❌":
            await ctx.send(f"{ctx.author.mention}, {member} Refused your request.")
            return
        if reaction.emoji == "✅":
            pass

        # Starting
        game = await db.Create.game(ctx.author.id, member.id)
        await db.Update.user(ctx.author.id, "playing", True, True)
        await db.Update.user(member.id, "playing", True, True)
        theme = await db.Get.theme(game)
        playerOne = await db.Get.user(ctx.author.id)

        # Game time
        startTime = datetime.utcnow()

        # Win rewards
        expAmt = random.randint(10,50)

        # On-going
        while (playerOne['playing']):

            # Game data
            game = await db.Get.game(game['id'])
            board = await Backend.prettierGame(game['id'])
            theme = await db.Get.theme(game)

            # Board embed
            embed = discord.Embed(title="Connect 4", description=f"Reply with `1`-`7` to place your move.\n{board}", color = int(theme['embedColor'], 16))
            if game['turn'] == ctx.author.id:
                embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author.mention} *`(Your turn!)`*", inline=False)
                embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member}", inline=False)
            else:
                embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author}", inline=False)
                embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member.mention} *`(Your turn!)`*", inline=False)
            embed.set_footer(text=f"ID: {game['id']} {default.footer(True)}")
            await ctx.send(embed=embed)

            # Move
            def check(message):
                return message.content in ['1','2','3','4','5','6','7'] and message.author.id == game['turn'] or message.content == 'quit' and message.author.id in game['players']

            try:
                move = await self.client.wait_for('message', check=check, timeout=300.0)

            except asyncio.TimeoutError:
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = int(theme['embedColor'], 16))
                if game['turn'] == ctx.author.id:
                    user, oponent = member, ctx.author
                    embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author} *`(Afk)`*", inline=False)
                    embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member.mention} *`(Winner!)`*", inline=False)
                else:
                    user, oponent = member, ctx.author
                    embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author.mention} *`(Winner!)`*", inline=False)
                    embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member} *`(Afk)`*", inline=False)
                await ctx.send(f"{user} ran away!")
                await db.Update.user(user.id, "loses", 1)
                await db.Update.user(oponent.id, "wins", 1)
                await db.Update.user(oponent.id, "exp", expAmt)
                embed.set_footer(text=f"ID: {game['id']} {default.footer(True)}")
                await ctx.send(embed=embed)
                await db.Update.game(game['id'], "status", "finished", True)
                break

            # Quit check
            if move.content.lower() == "quit":
                msg = await ctx.send(f"{move.author.mention}, Respond with the game id to confirm your request.")

                def check(m):
                    return m.content.strip() == game['id'] and m.author.id in game['players']

                try:
                    msg = await self.client.wait_for('message', check=check, timeout=30) 
                except asyncio.TimeoutError:
                    await msg.delete()
                    await ctx.send(f"{move.author.mention}, You didn't respond in time, Request timed out.",delete_after=3)
                    continue
                else:
                    opponent = [id for id in game['players'] if msg.author.id != id]
                    await db.Delete.game(msg.content.lower())
                    await db.Update.user(ctx.author.id, "playing", False, True)
                    await db.Update.user(member.id, "playing", False, True)
                    await db.Update.user(msg.author.id, "loses", 1)
                    await db.Update.user(opponent[0], "wins", 1)
                    await db.Update.user(opponent[0], "exp", expAmt)
                    M = await self.client.fetch_user(opponent[0])
                    await ctx.send(f"{M.mention}, Won!")
                    return

            else: pass

            move = move.content

            # Move check
            if move > '7' or int(move) < 1: await ctx.send("Choose a valid column!")

            # Move play
            result = await Backend.playMove(game['id'], int(move)-1)
            while not (result):

                # Invalid column message

                await ctx.send("Choose a valid column!")

                # Move
                def check(message):
                    return message.content in ['1','2','3','4','5','6','7'] and message.author.id == game['turn']
                try:
                    move = await self.client.wait_for('message', check=check, timeout=300.0)
                except asyncio.TimeoutError:
                    embed = discord.Embed(title="Connect 4", description=f"{board}", color = int(theme['embedColor'], 16))
                    if game['turn'] == ctx.author.id:
                        user, oponent = ctx.author, member
                        embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author} *`(Afk)`*", inline=False)
                        embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member.mention} *`(Winner!)`*", inline=False)
                    else:
                        user, oponent = member, ctx.author
                        embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author.mention} *`(Winner!)`*", inline=False)
                        embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member} *`(Afk)`*", inline=False)
                    await ctx.send(f"{user} ran away!")
                    await db.Update.user(user.id, "loses", 1)
                    await db.Update.user(oponent.id, "wins", 1)
                    await db.Update.user(oponent.id, "exp", expAmt)
                    embed.set_footer(text=f"ID: {game['id']} {default.footer(True)})")
                    await ctx.send(embed=embed)
                    await db.Update.game(game['id'], "status", "finished", True)
                    break
                else: pass
                move = move.content

                # Move check
                if move > '7' or int(move) < 1: await ctx.send("Choose a valid column!")

                # Move play
                result = await Backend.playMove(game['id'], int(move)-1)

            # Game data
            game = await db.Get.game(game['id'])
            board = await Backend.prettierGame(game['id'])

            # Game checks
            #- Draw check
            if await Backend.drawCheck(game['id']):
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = int(theme['embedColor'], 16))
                embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author.mention} *`(Draw!)`*", inline=False)
                embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member.mention} *`(Draw!)`*", inline=False)
                embed.set_footer(text=f"ID: {game['id']} {default.footer(True)}")
                await ctx.send(embed=embed)
                await db.Update.game(game['id'], "status", "finished", True)
                await db.Update.user(ctx.author.id, "draws", 1)
                await db.Update.user(member.id, "draws", 1)
                break

            #- Win check
            if await Backend.winCheck(game['id']):
                board = await Backend.prettierGame(game['id'])
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = int(theme['embedColor'], 16))
                if game['turn'] == ctx.author.id:
                    embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author.mention} *`(Winner!)`*", inline=False)
                    embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member}", inline=False)
                else:
                    embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author}", inline=False)
                    embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member.mention} *`(Winner!)`*", inline=False)
                embed.set_footer(text=f"ID: {game['id']} {default.footer(True)}")
                await ctx.send(embed=embed)
                await db.Update.game(game['id'], "status", "finished", True)
                await db.Update.user(game['turn'], "wins", 1)
                await db.Update.user(game['turn'], "exp", expAmt)
                loser = 1
                if game['players'].index(game['turn']) == 1: 
                    loser == 0 
                await db.Update.user(game['players'][loser], "loses", 1)
                break

            # Turn switch
            if game['turn'] == ctx.author.id:
                await db.Update.game(game['id'], "turn", member.id, True)
            else:
                await db.Update.game(game['id'], "turn", ctx.author.id, True)


        # Finished!
        await db.Update.user(ctx.author.id, "playing", False, True)
        await db.Update.user(member.id, "playing", False, True)

        # Delete game
        await db.Delete.game(game['id'])

        # Game time
        timeSpent = datetime.utcnow() - startTime
        await ctx.send(f"Time spent: {humanize.precisedelta(timeSpent)}", delete_after=10)
    
    @commands.group(invoke_without_command=True)
    async def lobby(self, ctx):
        embed = default.Embed.maintenance()
        await ctx.send(embed=embed); return
        lData = await db.Lobby.fetch()
        fields = []
        for key, value in lData.items():
            user = await self.client.fetch_user(key)
            fields.append(f"{user.name}\s Rank: {HL(value['rank'])}\s False")
        embed = default.Embed.custom("Connect 4 - Lobby", None, default.Color.blurple, fields, None, f"Players: {len(lData)}")
        await ctx.send(embed=embed)
    
    @lobby.command()
    async def join(self, ctx):
        embed = default.Embed.maintenance()
        await ctx.send(embed=embed); return
        lData = await db.Lobby.fetch()
        if ctx.author.id in lData.keys():
            embed = default.Embed.error("InLobby", f"{ctx.author.mention}, You're already in lobby. (In-lobby: {len(lData)})")
            await ctx.send(embed=embed)
            return
        uData = await db.Get.user(ctx.author.id)
        await db.Lobby.update(ctx.author.id, "rank", db.Get.rank(uData['points']), True)
        embed = default.Embed.success("Joined", f"{ctx.author.mention}, You've joined the lobby, Your game will be started when a worthy opponent is found. (In-lobby: {len(lData)})")
        await ctx.send(embed=embed)
    
    @lobby.command()
    async def leave(self, ctx):
        embed = default.Embed.maintenance()
        await ctx.send(embed=embed); return
        lData = await db.Lobby.fetch()
        if ctx.author.id not in lData.keys():
            embed = default.Embed.error("NotInLobby", f"{ctx.author.mention}, You're not in lobby.")
            await ctx.send(embed=embed)
            return
        await db.Lobby.delete(ctx.author.id)
        embed = default.Embed.success("Left", f"{ctx.author.mention}, You've left the lobby.")
        await ctx.send(embed=embed)


    @commands.command(aliases=['inv'], help="Displays a specific member's or the user's inventory.")
    async def inventory(self, ctx, member : typing.Optional[discord.Member] = None):
        user = ctx.author
        if (member): user = member

        items = await db.Fetch.items()
        data = await db.Get.inventory(user.id)
        
        embed = discord.Embed(title="Connect 4 - Inventory", colour = user.top_role.color)
        
        for child, value in data.items():
            Name = f"**{fix(child)}** `({len(data[child])}/{len(items[child])})`:\n"
            Value = ""
            
            for key, value in value.items():
                if child == "embedColors":
                    Value += f"{fix(key)}: `{value}`\n"
                else:
                    Value += f"{value} {fix(key)}\n"
            embed.add_field(name=Name, value=Value, inline = False)
        embed.set_footer(text= f"{default.footer()}")
        msg = await ctx.send(embed=embed)

        await msg.add_reaction("🤏")

        def check(reaction, u):
            return reaction.emoji == "🤏" and u == user
        
        try:
            reaction, u = await self.client.wait_for('reaction_add', check=check, timeout=300)
        except asyncio.TimeoutError:
            await msg.delete()
            return

        if reaction.emoji == "🤏":
            await ctx.send(f"What would you like to use?")
            def check(m):
                um = unfix(m.content.lower())
                return um in data['discs'].keys() or um in data['backgrounds'].keys() or um in data['embedColors'].keys() and m.author == ctx.author

            try:
                msg = await self.client.wait_for('message', check=check, timeout=150)
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send(f"{user.mention}, You didn't respond in time, Request timedout.", delete_after=5)
                return

            msg = unfix(msg.content.lower())

            while True:

                # Disc
                if msg in data['discs'].keys():
                    await ctx.send(f"Would you like to use that as your `primary` or `secondary` disc?")
                    def check(m):
                        return m.content.lower() in ['primary', 'secondary'] and m.author == ctx.author

                    try:
                        msg2 = await self.client.wait_for('message', check=check, timeout=150)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        await ctx.send(f"{user.mention}, You didn't respond in time, Request timedout.", delete_after=5)
                        break; return

                    await db.Update.user(ctx.author.id, f'{msg2.content.lower()}Disc', data['discs'][msg], True)
                    await ctx.send(f"New {msg2.content.lower()} disc: {data['discs'][msg]}")
                    break
                
                # Background
                elif msg in data['backgrounds'].keys():
                    await db.Update.user(ctx.author.id, 'background', data['backgrounds'][msg], True)
                    await ctx.send(f"New background: {data['backgrounds'][msg]}")
                    break

                # Embed color
                elif msg in data['embedColors'].keys():
                    await db.Update.user(ctx.author.id, 'embedColor', str(data['embedColors'][msg]), True)
                    embed = discord.Embed(description = f"New embed color: `{data['embedColors'][msg]}`", color = int(data['embedColors'][msg], 16))
                    await ctx.send(embed=embed)
                    break
                    
                else:
                    await ctx.send("Choose a valid item!")

        else:
            pass


    @commands.command(aliases=['p'], help="Displays a specific member's or the user's profile.")
    async def profile(self, ctx, member : typing.Optional[discord.Member]):
        user = ctx.author
        if (member):
            user = member
        data = await db.Get.user(user.id)
        embed = discord.Embed(color = int(data['embedColor'], 16))
        embed.set_author(name = user)
        embed.set_thumbnail(url = user.avatar_url)
        embed.add_field(name="Level:", value=data['level'], inline=True)
        embed.add_field(name="Rank:", value=db.Get.rank(int(data['points'])), inline=True) #- Make rank
        embed.add_field(name="Coins:", value=f"{HL(data['coins'])}", inline=True)
        embed.add_field(name=f"Games played: ({HL(int(data['wins'] + data['draws'] + data['loses']))})", value=f"{B(data['wins'])} Wins | {B(data['draws'])} Draws | {B(data['loses'])} Loses", inline=False)
        embed.add_field(name="Primary disc:", value=f"{data['primaryDisc']} {HL(fix(data['primaryDisc']))}", inline=True)
        embed.add_field(name="Secondary disc:", value=f"{data['secondaryDisc']} {HL(fix(data['secondaryDisc']))}", inline=True)
        embed.add_field(name="Background:", value=f"{data['background']} {HL(fix(data['background']))}", inline=False)
        embed.add_field(name="Embed color:", value=f"{HL(data['embedColor'])}", inline=False)
        embed.set_footer(text = f"Exp: {round(int(data['exp']))} / {round((int(data['level']) * 4.231) * 100)} {default.footer(True)}")
        await ctx.send(embed=embed)


    @commands.command(aliases=['htp', 'howtoplay'], name='how-to-play', help="Detailed explaination to how the game works.")
    async def how_to_play(self, ctx, page : typing.Optional[int] = None):
        if not (page): page = 0
        rs = ['⏮️', '◀️', '⏹️', '▶️', '⏭️']

        embeds = [
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
            default.Embed.custom("How To Play", None, default.Color.blurple, None, None, None, None, None),
        ]

        embeds[page].set_footer(text=f"Page: {page} / {len(embeds)} {default.footer(True)}")
        msg = await ctx.send(embed=embeds[page])
        [await msg.add_reaction(r) for r in rs]

        while True:
            def check(reaction, user):
                return str(reaction.emoji) in rs and user == ctx.author

            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=120)
            except asyncio.TimeoutError:
                await msg.delete(); break
            else:
                if str(reaction.emoji) == '⏮️' and page != 0:
                    page == 0; pass
                elif str(reaction.emoji) == '◀️' and page != 0:
                    page -= 1; pass
                elif str(reaction.emoji) == '⏹️':
                    await msg.delete(); break
                elif str(reaction.emoji) == '▶️' and page != len(embeds):
                    page += 1; break
                elif str(reaction.emoji) == '⏭️' and page != len(embeds):
                    page = len(embeds); break
                else:
                    continue
            
            embeds[page].set_footer(text=f"Page: {page} / {len(embeds)} {default.footer(True)}")
            await msg.edit(embed=embeds[page])
            await msg.clear_reactions()
            [await msg.add_reaction(r) for r in rs]
            



def setup(client):
    client.add_cog(Game(client))