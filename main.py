import discord
import logging
import logging.handlers

import settings

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
        print(f'DEBUG MODE')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if  __debug__:
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

    if message.content.startswith('!W'):
        await message.channel.send('fk matteo')

    if message.content == '!matteo':
        await message.channel.send('smh')

client.run(settings.DISCORD_TOKEN, log_handler=None)