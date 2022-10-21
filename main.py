from email.mime import base
import discord
import logging
import logging.handlers
import settings
import random

from models.wins import Win
from models.honing import createTable, uploadData
from db_connection import Session
from commands import win_commands, loss_commands, lookup_commands
from util.honing.honing_calculator import calculate_honing, list_all_hones, calculate_attempts_from_artisans
from util.command_parser import parse_multiple

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
    print(f'Logged in as {client.user}')
    if  __debug__:
        # createTable()
        # uploadData()
        #print(calculate_attempts_from_artisans(0.05, 0.005, 0.1, 100))
        print(f'DEBUG MODE')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if  __debug__:
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

    # Message startswith
    if message.content.startswith('!W'):
        #await win_commands.add_win(message)
        await message.channel.send("Command deprecated. If it's a honing W, try !honing command")
    
    if message.content.startswith("!L"):
        #await loss_commands.add_loss(message)
        await message.channel.send("Command deprecated. If it's a honing L, try !honing command")

    if message.content.startswith('!lookup'):
        if message.content == '!lookup help':
            await lookup_commands.lookup_help(message)
        else:
            await lookup_commands.lookup(message)
            
    if message.content == "!myHones":
        await list_all_hones(message)
            
    if message.content.startswith("!honing"):
        parsedMessage = parse_multiple(message)
        #Todo: Implement pity parsing
        if (parsedMessage[-1] != "armor" and parsedMessage[-1] != "weapon"):
            await message.channel.send("Error parsing type of gear. The last word must be either 'weapon' or 'armor'")
        if (parsedMessage[1] == "tap"):
            try:
                numberOfTaps = int(parsedMessage[0])
                targetGearLvl = int(parsedMessage[-2])
                gearPiece = parsedMessage[-1]
                await message.channel.send(calculate_honing(message, targetGearLvl, numberOfTaps, gearPiece))
            except Exception as e:
                await message.channel.send(e)
        # Example: 80.32 artisans 19 armor
        elif (parsedMessage[1] == "artisans"):
            try:
                targetGearLvl = int(parsedMessage[-2])
                gearPiece = parsedMessage[-1]
                numberOfTaps = calculate_attempts_from_artisans(float(parsedMessage[0]), targetGearLvl, gearPiece)
                await message.channel.send(calculate_honing(message, targetGearLvl, numberOfTaps, gearPiece))
            except Exception as e:
                await message.channel.send(e)
        elif (parsedMessage[0] == "pitied"):
            try:
                await message.channel.send("Pity functionality not implemented yet")
            except Exception as e:
                await message.channel.send(e)
        else:
            pass

    # Message matches
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