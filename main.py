import discord, asyncio, os, humanize
from discord.ext import commands
from func import database as db
from dotenv import load_dotenv
from datetime import datetime, timedelta
from func import default

load_dotenv('func\.env')

# Prefix
async def prefix(bot, message):
    # print(message)
    data = await db.Get.guild(message.guild.id)
    # if message.author.id == default.developer() and message.content.lower() == f"beta{data['prefix']}":
    #     return f"beta{data['prefix']}"
    return data['prefix']

# Intents
intents = discord.Intents.default()
intents.guilds=True
intents.members=True
intents.reactions=True
intents.voice_states=True

# Client
client = commands.Bot(command_prefix=prefix, case_sensitive=True, intents=intents)


# On ready event
@client.event
async def on_ready():
    print("running...")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f"connect-4.exe"))


# Prefix command
@client.group(invoke_without_command=True)
async def prefix(ctx):
    data = await db.Get.guild(ctx.guild.id)
    await ctx.send(f"Current guild prefix: `{data['prefix']}`")

# Update prefix subcommand
@prefix.command(aliases=['u'])
@commands.has_permissions(manage_guild=True)
async def update(ctx, prefix : str):
    if len(prefix) > 3 or len(prefix) < 1: await ctx.send(f"Your prefix must be `1`-`3` characters long"); return
    await db.Update.guild(ctx.guild.id, "prefix", prefix, True)
    await ctx.send(f"Your prefix has been updated!\nNew prefix: `{prefix}`")

# Update error handler
@update.error
async def update_error(ctx, error):
    data = await db.Get.guild(ctx.guild.id)
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, This command requires the "`Manage Server`" permission.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, `prefix` is a required argument that is missing.\n`{data['prefix']}prefix update|u (member)`")
    else: await ctx.send(f"{ctx.author.mention}, Something went wrong but I can't seem to figure it out. For further assistance visit our [support server](https://discord.gg/WZw6BV5YCP)")


# On message event
@client.event
async def on_message(message):
    data = await db.Get.guild(message.guild.id)
    if client.user.mentioned_in(message):
        if not message.content.startswith(data['prefix']): await message.channel.send(f"Current server prefix: `{data['prefix']}`")
        return
    
    await client.process_commands(message)


# Discord terminal
async def discordTerminal(msg):
    msg = str(msg)
    channel = await client.fetch_channel(default.terminal())
    msg = [msg[i:i+2048] for i in range(0, len(msg), 2048)]
    await channel.send(f"```cmd\n{msg}\n```")


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
@client.command()
async def play(ctx, member : discord.Member):
    # Checks
    if member == ctx.author: await ctx.send("No. Just.. No"); return
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

    # On-going
    while (playerOne['playing']):



        print("On-going")

        # Game data
        game = await db.Get.game(game['id'])
        board = await prettierGame(game['id'])

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
            return message.content in ['1','2','3','4','5','6','7'] and message.author.id == game['turn']
        try:
            move = await client.wait_for('message', check=check, timeout=300.0)
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
            embed.set_footer(text=f"ID: {game['id']} {default.footer(True)}")
            await ctx.send(embed=embed)
            await db.Update.game(game['id'], "status", "finished", True)
            break
        else: pass
        move = move.content

        print("Move")

        # Move check
        if move > '7' or int(move) < 1: await ctx.send("Choose a valid column!")

        print("Move check")

        #! Quit check
        # prefix = await prefix()

        # def check(m):
        #     return m.content.lower() in [f"{prefix}quit", "quit"] and m.author in game['players']

        # try:
        #     msg = await client.wait_for('message', check=check)
        # except asyncio.TimeoutError:
        #     pass

        # if msg.content.lower() in [f"{prefix}quit", "quit"]:
        #     msg = await ctx.send(f"{ctx.author.mention}, Respond with the game id to confirm your request.")
        #     def check(m):
        #         return m.content.strip() == game['id'] and m.author.id in game['players']

        #     try:
        #         msg = await client.wait_for('message', check=check, timeout=30) 
        #     except asyncio.TimeoutError:
        #         await msg.delete()
        #         msg2 = await ctx.send(f"{ctx.author.mention}, You didn't respond in time, Request timed out.")
        #         await asyncio.sleep(3)
        #         await msg2.delete()
        #         pass
        #     else:
        #         await ctx.send(f"Game (`{msg.content}`) is not a valid game.")

        #     opponent = [id for id in game['players'] if msg.author.id != id]
        #     await db.Delete.game(msg.content.lower())
        #     await db.Update.user(ctx.author.id, "playing", False, True)
        #     await db.Update.user(member.id, "playing", False, True)
        #     await db.Update.user(msg.author.id, "loses", 1)
        #     await db.Update.user(opponent[0], "wins", 1)
        #     member = await client.fetch_user(opponent)
        #     await ctx.send(f"{member.mention}, Won!")
        #     return
        
        # else: pass

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
            result = await playMove(game['id'], int(move)-1)

        print("Move play")

        # Game data
        game = await db.Get.game(game['id'])
        board = await prettierGame(game['id'])

        print("Game data")

        # Game checks
        #- Draw check
        if await drawCheck(game['id']):
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
        if await winCheck(game['id']):
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
    await ctx.send(f"Time spent: {humanize.precisedelta(timeSpent)}")

    print("Game time")

    print("Finished")

@play.error
async def play_error(ctx, error):
    data = await db.Get.guild(ctx.guild.id)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, `member` is a required argument that is missing.\n`{data['prefix']}play (member)`")
    else:
        await ctx.send(f"{ctx.author.mention}, Something went wrong but I can't seem to figure it out. For further assistance visit our support server\n(https://discord.gg/WZw6BV5YCP)")
        await discordTerminal(error)


@client.command(aliases=['c'])
async def color(ctx, clr):
    embed = discord.Embed(description = clr, color= int(str(clr), 16))
    embed.set_footer(default.footer())
    await ctx.send(embed=embed)


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