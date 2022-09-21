import discord
import settings


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    if __debug__:
        print(f'DEBUG MODE')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if __debug__:
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

    if message.content.startswith('!W'):
        await message.channel.send('fk matteo')

    if message.content == '!matteo':
        await message.channel.send('smh')

client.run(settings.DISCORD_TOKEN)