import logging
import logging.handlers
from email.mime import base

import discord

import settings
from commands import (honing_commands, lookup_commands, loss_commands,
                      party_commands, win_commands)
from util.command_parser import parse_multiple, parse_prune
from util.constants import GEAR_TIER, GEAR_TYPE
from util.honing.honing_calculator import (list_all_hones, HoningCalculator)
from util.honing.honing_strategies import *
from util.honing.honing_data_manipulator import *

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
honingDataManipulator = HoningDataManipulator()

"""
Events
"""
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    #test.set_honing_strategy(GEAR_TIER["brel"], GEAR_TYPE["weapon"])
    
    #print(test.honing_strategy.calculate_gold_value_of_materials_used("13", 9))
    #test.delete_last_hone(179710669761937408)
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
            
    if message.content == "!graphHones":
        await honing_commands.graph_hones(message, honingDataManipulator)
        
    if message.content == "!deleteLastHone":
        targetLevel, numTaps, gearType = honingDataManipulator.delete_last_hone(message.author.id)
        await message.channel.send("Deleted your last hone where you {} tapped {} {}".format(numTaps, targetLevel, gearType.name))

    if message.content.startswith("!honing"):
        parsedMessage = parse_multiple(message)
        #Todo: Implement pity parsing
        if (parsedMessage[-1] != "armor" and parsedMessage[-1] != "weapon"):
            await message.channel.send("Error parsing type of gear. The last word must be either 'weapon' or 'armor'")
        if (parsedMessage[-2] != "brel" and parsedMessage[-2] != "argos"):
            await message.channel.send("Error parsing tier of gear. The second last word must be either 'brel' or 'argos'")
        targetGearHoningTier = parsedMessage[-2] # brel/argos
        gearPiece = parsedMessage[-1] # weapon/armor
        targetGearLvl = parsedMessage[-3] # 19
        #honingDataManipulator.set_honing_strategy(GEAR_TIER[targetGearHoningTier], GEAR_TYPE[gearPiece])
        # Example: 20 tap 19 brel weapon
        if (parsedMessage[1] == "tap"):
            try:
                numberOfTaps = int(parsedMessage[0]) # 20
                data = honingDataManipulator.commit_honing_to_db(message, targetGearLvl, numberOfTaps, GEAR_TIER[targetGearHoningTier], GEAR_TYPE[gearPiece])
                await message.channel.send(honingDataManipulator.honing_strategy.compose_honing_message(data, numberOfTaps))
            except Exception as e:
                await message.channel.send(e)
        # Example: 80.32 artisans 19 brel armor
        elif (parsedMessage[1] == "artisans"):
            try:
                honingDataManipulator.set_honing_strategy(GEAR_TIER[targetGearHoningTier], GEAR_TYPE[gearPiece])
                numberOfTaps = honingDataManipulator.honing_strategy.convert_artisans_to_num_taps(targetGearLvl, float(parsedMessage[0]))
                data = honingDataManipulator.commit_honing_to_db(message, targetGearLvl, numberOfTaps, GEAR_TIER[targetGearHoningTier], GEAR_TYPE[gearPiece])
                await message.channel.send(honingDataManipulator.honing_strategy.compose_honing_message(data, numberOfTaps))
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
        await message.channel.send(party_commands.get_phrase(parse_prune(message)))

    if message.content == '!kunge':
        await message.channel.send(party_commands.get_phrase(parse_prune(message)))

    if message.content == "!clown":
        await message.channel.send(party_commands.get_phrase(parse_prune(message)))
        
    if message.content == "!myWs":
        await win_commands.list_wins(message)
        
    if message.content == "!myLs":
        await loss_commands.list_losses(message)

    if message.content == "!clearWs":
        await win_commands.clear_wins(message)

    if message.content == "!clearLs":
        await loss_commands.clear_losses(message)

client.run(settings.DISCORD_TOKEN, log_handler=None)
