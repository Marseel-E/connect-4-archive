import discord, os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv('.\\func\.env')

intents = discord.Intents.all()
client = commands.Bot(command_prefix="a", case_sensitive=True, intents=intents)


@client.event
async def on_ready():
    print("[Messenger]: Starting..")
    print("[Messenger]: _quit - Leave the current running loop.")
    channelId = input("[Messenger]: Channel ID: ")
    if channelId.lower() == "_quit": await client.logout()
    channel = await client.fetch_channel(channelId)
    while True:
        message = input("[Messenger]: ")
        if message.lower() == "_quit": break
        await channel.send(message)
    await client.logout()


client.run(os.environ.get("TOKEN"))