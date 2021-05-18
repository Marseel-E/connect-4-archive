import discord, sys, traceback, pyrebase, typing, asyncio, os
from discord.client import Client
from discord.user import ClientUser
from discord.ext import commands
from io import StringIO
import database as db
from dotenv import load_dotenv

load_dotenv('.env')

# Prefix
async def prefix(bot, message):
    data = await db.Get.guild(message.guild.id)
    return data['prefix']

intents = discord.Intents.all()
client = commands.Bot(command_prefix=prefix, case_sensitive=True, intents=intents)

print("Prefix")

@client.event
async def on_ready():
    print("running...")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f"connect-4.exe"))


@client.group(invoke_without_command=True)
async def prefix(ctx):
    data = await db.Get.guild(ctx.guild.id)
    await ctx.send(f"Current guild prefix: `{data['prefix']}`")

@prefix.command(aliases=['u'])
@commands.has_permissions(manage_guild=True)
async def update(ctx, prefix : str):
    if len(prefix) > 3 or len(prefix) < 1: await ctx.send(f"Your prefix must be `1`-`3` characters long"); return
    await db.Update.guild(ctx.guild.id, "prefix", prefix, True)
    await ctx.send(f"Your prefix has been updated!\nNew prefix: `{prefix}`")

@update.error
async def update_error(ctx, error):
    data = await db.Get.guild(ctx.guild.id)
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, This command requires the "`Manage Server`" permission.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, `prefix` is a required argument that is missing.\n`{data['prefix']}prefix update|u (member)`")
    else: await ctx.send(f"{ctx.author.mention}, Something went wrong but I can't seem to figure it out. For further assistance visit our [support server](https://discord.gg/WZw6BV5YCP)")


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        data = await db.Get.guild(message.guild.id)
        await message.channel.send(f"Current server prefix: `{data['prefix']}`"); return
    
    await client.process_commands(message)


@client.command()
async def py(ctx, unformatted : typing.Optional[bool] = False, *, cmd):
    if ctx.author.id not in [470866478720090114]: return
    await ctx.message.delete()
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

    # Opponent
    msg = await ctx.send(f"{member.mention}, {ctx.author} invited you to a Connect 4 game would you like to play?")
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return user == member and str(reaction.emoji) in ["✅", "❌"]
    try:
        reaction, user = await client.wait_for('reaction_add', check=check, timeout=150.0)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, {member} didn't respond in time. Request timedout!")
        return
    
    if reaction.emoji == "❌":
        await ctx.send(f"{ctx.author.mention}, {member} Refused your request.")
        return
    elif reaction.emoji == "✅":
        pass
    else: pass

    print("Opponent")

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
            embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author} *`(Your turn!)`*", inline=False)
            embed.add_field(name=":yellow_circle: Player 2", value=f"{member}", inline=False)
        else:
            embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author}", inline=False)
            embed.add_field(name=":yellow_circle: Player 2", value=f"{member} *`(Your turn!)`*", inline=False)
        embed.set_footer(text=f"ID: {game['id']}")
        await ctx.send(embed=embed)
        
        print("Board embed")

        # Move
        def check(message):
            return message.content in ['1','2','3','4','5','6','7'] and message.author.id == game['turn']
        try:
            move = await client.wait_for('message', check=check, timeout=300.0)
        except asyncio.TimeoutError:
            if game['turn'] == ctx.author.id:
                await ctx.send(f"{ctx.author} ran away!")
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0x00FF00)
                embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author} *`(Afk)`*", inline=False)
                embed.add_field(name=":yellow_circle: Player 2", value=f"{member} *`(Winner!)`*", inline=False)
                await db.Update.user(ctx.author.id, "loses", 1)
                await db.Update.user(member.id, "wins", 1)
            else:
                await ctx.send(f"{member} ran away!")
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0xFF0000)
                embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author} *`(Winner!)`*", inline=False)
                embed.add_field(name=":yellow_circle: Player 2", value=f"{member} *`(Afk)`*", inline=False)
                await db.Update.user(member.id, "loses", 1)
                await db.Update.user(ctx.author.id, "wins", 1)
            embed.set_footer(text=f"ID: {game['id']}")
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
        result = await playMove(game['id'], int(move)-1)
        while not (result):

            # Invalid column message

            await ctx.send("Choose a valid column!")

            print("Invalid column message")

            # Move
            def check(message):
                return message.content in ['1','2','3','4','5','6','7'] and message.author.id == game['turn']
            try:
                move = await client.wait_for('message', check=check, timeout=300.0)
            except asyncio.TimeoutError:
                if game['turn'] == ctx.author.id:
                    await ctx.send(f"{ctx.author} ran away!")
                    embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0x00FF00)
                    embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author} *`(Afk)`*", inline=False)
                    embed.add_field(name=":yellow_circle: Player 2", value=f"{member} *`(Winner!)`*", inline=False)
                    await db.Update.user(ctx.author.id, "loses", 1)
                    await db.Update.user(member.id, "wins", 1)
                else:
                    await ctx.send(f"{member} ran away!")
                    embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0xFF0000)
                    embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author} *`(Winner!)`*", inline=False)
                    embed.add_field(name=":yellow_circle: Player 2", value=f"{member} *`(Afk)`*", inline=False)
                    await db.Update.user(member.id, "loses", 1)
                    await db.Update.user(ctx.author.id, "wins", 1)
                embed.set_footer(text=f"ID: {game['id']}")
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
            result = await playMove(game['id'], int(move)-1)

        print("Move play")

        # Game data
        game = await db.Get.game(game['id'])
        board = await prettierGame(game['board'])

        print("Game data")

        # Game checks
        #- Draw check
        if await drawCheck(game['id']):
            embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0xFFFF00)
            embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author} *`(Draw!)`*", inline=False)
            embed.add_field(name=":yellow_circle: Player 2", value=f"{member} *`(Draw!)`*", inline=False)
            embed.set_footer(text=f"ID: {game['id']}")
            await ctx.send(embed=embed)
            await db.Update.game(game['id'], "status", "finished", True)
            await db.Update.user(ctx.author.id, "draws", 1)
            await db.Update.user(member.id, "draws", 1)

            print("Draw check"); break

        #- Win check
        if await winCheck(game['id']):
            if game['turn'] == ctx.author.id:
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0x00FF00)
                embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author} *`(Winner!)`*", inline=False)
                embed.add_field(name=":yellow_circle: Player 2", value=f"{member}", inline=False)
            else:
                embed = discord.Embed(title="Connect 4", description=f"{board}", color = 0xFF0000)
                embed.add_field(name=":blue_circle: Player 1", value=f"{ctx.author}", inline=False)
                embed.add_field(name=":yellow_circle: Player 2", value=f"{member} *`(Winner!)`*", inline=False)
            embed.set_footer(text=f"ID: {game['id']}")
            await ctx.send(embed=embed)
            await db.Update.game(game['id'], "status", "finished", True)
            await db.Update.user(game['turn'], "wins", 1)
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

    print("Finished")

@play.error
async def play_error(ctx, error):
    data = await db.Get.guild(ctx.guild.id)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, `member` is a required argument that is missing.\n`{data['prefix']}play (member)`")
    else: await ctx.send(f"{ctx.author.mention}, Something went wrong but I can't seem to figure it out. For further assistance visit our [support server](https://discord.gg/WZw6BV5YCP)")

client.run(os.environ.get("TOKEN"))