import discord, sys, traceback, pyrebase, typing
from discord.ext import commands
from io import StringIO
import database as db

prefix = "-"

intents = discord.Intents.all()
client = commands.Bot(command_prefix=prefix, intents=intents)


@client.event
async def on_ready():
    print("running...")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("connect-4.exe|-help"))


@client.command()
async def py(ctx, unformatted : typing.Optional[bool] = False, *, cmd):
    if ctx.author.id != ctx.guild.owner_id: return
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    try:
        exec(str(cmd))
    except Exception as e:
        traceback.print_stack(file=sys.stdout)
        print(sys.exc_info())
    sys.stdout = old_stdout
    if (unformatted):
        await ctx.send(redirected_output.getvalue())
    else:
        embed = discord.Embed(title=f"Input:\n```py\n{cmd}\n```", description=f"Output:\n`{redirected_output.getvalue()}`", color = 0xFFFFFF)
        await ctx.send(embed=embed)


async def playMove(gameId, column):
    game = await db.Get.game(gameId)
    board = game['board']
    player = (game['players'].index(game['turn']) + 1)
    for row in reversed(range(len(board))):
        if board[row][int(column)] == '0': board[row][int(column)] = str(player); await db.Update.game(gameId, "board", board, True); break
        elif row == 0:
            if player == 1: await db.Update.game(gameId, "turn", game['players'][player+1], True)
            else: await db.Update.game(gameId, "turn", game['players'][player-1], True)
        else: pass

async def winCheck(gameId):
    game = await db.Get.game(gameId)
    board = game['board']
    player = (game['players'].index(game['turn']) + 1)
    print(f"[winCheck]: checking player {player}")
    won = True
    for row in range(len(board)):
        for col in range(len(board[row])):

            if col == 0:
                if board[row][col] == str(player):

                    # Horizontal
                    if board[row][col+1] == str(player) and board[row][col+2] == str(player) and board[row][col+3] == str(player): won = False

                    # Vertical
                    if row < 3:
                        if board[row+1][col] == str(player) and board[row+2][col] == str(player) and board[row+3][col] == str(player): won = False

                    # ascend
                    if row <= 3:
                        if board[row+1][col+1] == str(player) and board[row+2][col+2] == str(player) and board[row+3][col+3] == str(player): won = False

                    # descend
                    if row >= 3:
                        if board[row-1][col+1] == str(player) and board[row-2][col+2] == str(player) and board[row-3][col+3] == str(player): won = False

            else: pass
    
    return won

async def drawCheck(gameId):
    game = await db.Get.game(gameId)
    board = game['board']
    for row in range(len(board)):
        for col in range(len(board[row])):

            if board[row][col] == '0': return False

    return True


async def prettierGame(board):
    newBoard = ""
    for row in range(len(board)):
        newBoard += f"\n"
        for col in range(len(board[row])):
            if board[row][col] == '0': newBoard += ":black_circle: "
            if board[row][col] == '1': newBoard += ":blue_circle: "
            if board[row][col] == '2': newBoard += ":yellow_circle: "
    return newBoard


@client.command()
async def play(ctx, member : discord.Member):
    
    # Checks
    playerOne = await db.Get.user(ctx.author.id)
    playerTwo = await db.Get.user(member.id)
    if (playerOne['playing']): await ctx.send(f"You're already playing a game!"); return
    if (playerTwo['playing']): await ctx.send(f"Your opponent is playing a game already!"); return
    
    print("Checks")

    # Starting
    game = await db.Create.game(ctx.author.id, member.id)
    await db.Update.user(ctx.author.id, "playing", True, True)
    await db.Update.user(member.id, "playing", True, True)
    
    print("Starting")

    # On-going
    while game['status'] != "finished" or game['status'] == "on-going":

        print("On-going")

        # Game data
        game = await db.Get.game(game['id'])
        board = await prettierGame(game['board'])

        print("Game data")

        # Board embed
        embed = discord.Embed(title="Connect 4", description=f"Reply with `1`-`7` to place your move.\n{board}", color = 0xFFFFFF)
        if game['turn'] == ctx.author.id:
            embed.add_field(name="Player 1", value=f"{ctx.author} *`(Your turn!)`*", inline=False)
            embed.add_field(name="Player 2", value=f"{member}", inline=False)
        else:
            embed.add_field(name="Player 1", value=f"{ctx.author}", inline=False)
            embed.add_field(name="Player 2", value=f"{member} *`(Your turn!)`*", inline=False)
        embed.set_footer(text=f"ID: {game['id']}")
        await ctx.send(embed=embed)
        
        print("Board embed")

        # Move
        def check(message):
            return message.content in ['1','2','3','4','5','6','7'] and message.author.id == game['turn']
        move = await client.wait_for('message', check=check)
        move = move.content

        print("Move")

        # Move check
        if int(move) > 7 or int(move) < 1: await ctx.send("Choose a valid column!")

        print("Move check")

        # Move play
        await playMove(game['id'], int(move)-1)

        print("Move play")

        # Game data
        game = await db.Get.game(game['id'])
        board = await prettierGame(game['board'])

        print("Game data")

        # Game checks
        #- Draw check
        if await drawCheck(game['id']):
            embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0xFFFF00)
            embed.add_field(name="Player 1", value=f"{ctx.author} *`(Draw!)`*", inline=False)
            embed.add_field(name="Player 2", value=f"{member} *`(Draw!)`*", inline=False)
            embed.set_footer(text=f"ID: {game['id']}")
            await ctx.send(embed=embed)
            await db.Update.game(game['id'], "status", "finished", True)
            await db.Update.user(ctx.author.id, "draws", 1)
            await db.Update.user(member.id, "draws", 1)
            await ctx.send(f"Draw!")

            print("Draw check"); break

        #- Win check
        if not await winCheck(game['id']):
            if game['turn'] == ctx.author.id:
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0x00FF00)
                embed.add_field(name="Player 1", value=f"{ctx.author} *`(Winner!)`*", inline=False)
                embed.add_field(name="Player 2", value=f"{member}", inline=False)
            else:
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0xFF0000)
                embed.add_field(name="Player 1", value=f"{ctx.author}", inline=False)
                embed.add_field(name="Player 2", value=f"{member} *`(Winner!)`*", inline=False)
            embed.set_footer(text=f"ID: {game['id']}")
            await ctx.send(embed=embed)
            await db.Update.game(game['id'], "status", "finished", True)
            await db.Update.user(game['turn'], "wins", 1)
            loser = 1
            if game['players'].index(game['turn']) == 1: 
                loser == 0
                await ctx.send(f"{ctx.author} won!")
            await db.Update.user(loser, "loses", 1)
            await ctx.send(f"{member} won!")
            
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

    print("Finished")


client.run('Nzk1MDk5NjkwNjA5Mjc5MDA2.X_EcSg.lXnadtvhkCWOFVb4WVpU4HN4-Sg')