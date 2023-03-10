import discord

from util import command_parser, constants
from util.embeds import create_embed
from util.lookup import lookup_handler, lookup_plotter


#Lookup Help
async def lookup_help(message):
    await message.channel.send("Supported item names: " + ', '.join(constants.SUPPORTED_ITEMS))

# Lookup singular item
async def lookup(message):
    # Generate item data dict from JSON
    itemStr = command_parser.parse_singular(message)
    if itemStr in constants.SUPPORTED_ITEMS:
        data = lookup_handler.get_item_lookup(itemStr).json()[0]
        lookup_plotter.plot_historic(data['shortHistoric'])

        embed = create_embed(data['name'], 'Current Average Price: ' + str(data['avgPrice']), discord.Colour.blue())
        embed.set_thumbnail(url = data['image'])
        embed.set_image(url="attachment://plot_lookup_historic.png")
        file = discord.File("./images/plot_lookup_historic.png", filename="plot_lookup_historic.png")
        
        await message.channel.send(file = file, embed=embed)
    else:
        await message.channel.send("Item not supported. Try \"!lookup help\"")
