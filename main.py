import discord
import logging
import logging.handlers
import settings
import random

from models.wins import Win
from db_connection import Session
from commands import win_commands, loss_commands

"""
Logging
"""
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
Client Setup
"""
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


"""
Events
"""
@client.event
async def on_ready():
    with Session() as sess:
        pass
    print(f'Logged in as {client.user}')
    if  __debug__:
        print(f'DEBUG MODE')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if  __debug__:
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

    if message.content.startswith('!W'):
        await win_commands.add_win(message)
    
    if message.content.startswith("!L"):
        await loss_commands.add_loss(message)

    if message.content == '!matteo':
        phrases = [
            "smh",
            "starcraft?",
            "nah sus",
            "pain",
            "I'm gonna pity this aren't I",
            "I don't know why my character doesn't do damage",
            "I enjoy breaking Andrew's mental"
        ]
        
        await message.channel.send(random.choice(phrases))
        
    if message.content == "!myWs":
        await win_commands.list_wins(message)
        
    if message.content == "!myLs":
        await loss_commands.list_losses(message)

    if message.content == "!clearWs":
        await win_commands.clear_wins(message)

    if message.content == "!clearLs":
        await loss_commands.clear_losses(message)

client.run(settings.DISCORD_TOKEN, log_handler=None)