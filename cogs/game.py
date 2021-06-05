import discord, asyncio, humanize, typing, random
from discord.ext import commands
from func import database as db
from func import default
from datetime import datetime, timedelta
from func.human import *


#! FIX
# Discord terminal
# async def discordTerminal(msg):
#     msg = str(msg)
#     channel = await client.fetch_channel(client.user, default.terminal())
#     msg = [msg[i:i+2048] for i in range(0, len(msg), 2048)]
#     await channel.send(f"```cmd\n{msg}\n```")


class Game(commands.Cog):
    def __init__(self, client):
        self.client = client


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
        print(f"[winCheck]: checking player {player}")
        columns = 7
        rows = 6

        # Horizontal
        for col in range(columns-3):
            for row in range(rows):
                if board[row][col] == str(player) and board[row][col+1] == str(player) and board[row][col+2] == str(player) and board[row][col+3] == str(player): return True

        # Vertical
        for col in range(columns):
            for row in range(rows-3):
                if board[row][col] == str(player) and board[row+1][col] == str(player) and board[row+2][col] == str(player) and board[row+3][col] == str(player): return True

        # Ascend
        for col in range(columns-3):
            for row in range(rows-3):
                if board[row][col] == str(player) and board[row+1][col+1] == str(player) and board[row+2][col+2] == str(player) and board[row+3][col+3] == str(player): return True

        # Descend
        for col in range(columns-3):
            for row in range(3,rows):
                if board[row][col] == str(player) and board[row-1][col+1] == str(player) and board[row-2][col+2] == str(player) and board[row-3][col+3] == str(player): return True
        
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
        return newBoard


    # Play command
    @commands.command(help="Play a game of Connect 4 against someone.")
    async def play(self, ctx, member : discord.Member):
        # Checks
        if (member.bot): return
        if member == ctx.author: await ctx.send("No. Just.. No, NO!"); return
        playerOne = await db.Get.user(ctx.author.id)
        playerTwo = await db.Get.user(member.id)
        if (playerOne['playing']): await ctx.send(f"You're already playing a game!"); return
        if (playerTwo['playing']): await ctx.send(f"Your opponent is playing a game already!"); return
        
        print("Checks")

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

        print("Opponent")

        # Starting
        game = await db.Create.game(ctx.author.id, member.id)
        await db.Update.user(ctx.author.id, "playing", True, True)
        await db.Update.user(member.id, "playing", True, True)
        theme = await db.Get.theme(game)
        playerOne = await db.Get.user(ctx.author.id)
        
        print("Starting")

        # Game time
        startTime = datetime.utcnow()

        print("Game time")

        # Win rewards
        expAmt = random.randint(10,50)

        print("Win rewards")

        # On-going
        while (playerOne['playing']):
            print("On-going")

            # Game data
            game = await db.Get.game(game['id'])
            board = await Game.prettierGame(game['id'])

            print("Game data")

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
            
            print("Board embed")

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
                    member = await self.client.fetch_user(opponent[0])
                    await ctx.send(f"{member.mention}, Won!")
                    return

            else: pass
            
            print("Quit check")

            move = move.content

            print("Move")

            # Move check
            if move > '7' or int(move) < 1: await ctx.send("Choose a valid column!")

            print("Move check")

            # Move play
            result = await Game.playMove(game['id'], int(move)-1)
            while not (result):

                # Invalid column message

                await ctx.send("Choose a valid column!")

                print("Invalid column message")

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

                print("Move")

                # Move check
                if move > '7' or int(move) < 1: await ctx.send("Choose a valid column!")

                print("Move check")

                # Move play
                result = await Game.playMove(game['id'], int(move)-1)

            print("Move play")

            # Game data
            game = await db.Get.game(game['id'])
            board = await Game.prettierGame(game['id'])

            print("Game data")

            # Game checks
            #- Draw check
            if await Game.drawCheck(game['id']):
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = int(theme['embedColor'], 16))
                embed.add_field(name=f"{theme['oneDisc']} Player 1", value=f"{ctx.author.mention} *`(Draw!)`*", inline=False)
                embed.add_field(name=f"{theme['twoDisc']} Player 2", value=f"{member.mention} *`(Draw!)`*", inline=False)
                embed.set_footer(text=f"ID: {game['id']} {default.footer(True)}")
                await ctx.send(embed=embed)
                await db.Update.game(game['id'], "status", "finished", True)
                await db.Update.user(ctx.author.id, "draws", 1)
                await db.Update.user(member.id, "draws", 1)

                print("Draw check"); break

            #- Win check
            if await Game.winCheck(game['id']):
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
                
                print("Win check"); break
            
            print("Game checks")

            # Turn switch
            if game['turn'] == ctx.author.id:
                await db.Update.game(game['id'], "turn", member.id, True)
            else:
                await db.Update.game(game['id'], "turn", ctx.author.id, True)
            
            print("Turn switch")


        # Finished!
        await db.Update.user(ctx.author.id, "playing", False, True)
        await db.Update.user(member.id, "playing", False, True)

        # Delete game
        await db.Delete.game(game['id'])

        print("Delete game")

        # Game time
        timeSpent = datetime.utcnow() - startTime
        await ctx.send(f"Time spent: {humanize.precisedelta(timeSpent)}", delete_after=10)

        print("Game time")

        print("Finished")

    @play.error
    async def play_error(self, ctx, error):
        data = await db.Get.guild(ctx.guild.id)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention}, `member` is a required argument that is missing.\n`{data['prefix']}play (member)`")
        else:
            await ctx.send(f"{ctx.author.mention}, Something went wrong but I can't seem to figure it out. For further assistance visit our support server\n(https://discord.gg/WZw6BV5YCP)")
            # await discordTerminal(error) #! FIX


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
                    await db.Update.user(ctx.author.id, 'embedColor', data['embedColors'][msg], True)
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
        embed.add_field(name="Rank:", value="Soon!", inline=True) #- Make rank
        embed.add_field(name="Coins:", value=f"**Æ**`{data['coins']}`", inline=True)
        embed.add_field(name=f"Games played: `({int(data['wins'] + data['draws'] + data['loses'])})`", value=f"**{data['wins']}** Wins | **{data['draws']}** Draws | **{data['loses']}** Loses", inline=False)
        embed.add_field(name="Primary disc:", value=f"{data['primaryDisc']} `{fix(data['primaryDisc'])}`", inline=True)
        embed.add_field(name="Secondary disc:", value=f"{data['secondaryDisc']} `{fix(data['secondaryDisc'])}`", inline=True)
        embed.add_field(name="Background:", value=f"{data['background']} `{fix(data['background'])}`", inline=False)
        embed.add_field(name="Embed color:", value=f"`{data['embedColor']}`", inline=False)
        embed.set_footer(text = f"Exp: {round(int(data['exp']))} / {round((int(data['level']) * 4.231) * 100)} {default.footer(True)}")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Game(client))