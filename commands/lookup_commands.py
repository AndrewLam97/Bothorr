from util import command_parser, constants
from util.lookup import lookup_handler
import discord

#Lookup Help
async def lookup_help(message):
    await message.channel.send("Supported item names: " + ', '.join(constants.SUPPORTED_ITEMS))

# Lookup singular item
async def lookup(message):
    # Generate item data dict from JSON
    itemStr = command_parser.parse_singular(message)
    if itemStr in constants.SUPPORTED_ITEMS:
        data = lookup_handler.get_item_data(itemStr).json()[0]

        embed = create_embed_item(data)

        await message.channel.send(embed=embed)
    else:
        await message.channel.send("Item not supported. Try \"!lookup help\"")

# Create embed for singular item
def create_embed_item(data):
    embed = discord.Embed(
        type = 'rich',
        title = data['name'],
        description = 'Average Price: ' + str(data['avgPrice']),
        color = discord.Colour.blue()
    )   
    embed.set_image(url = data['image'])
    return embed