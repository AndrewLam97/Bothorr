import discord

from util import constants
from util.embeds import create_embed
from util.honing import honing_calculator, honing_plotter
from util.lookup import lookup_handler

priceMap = {}
for i in constants.SUPPORTED_ITEMS:
    if i in ["destruction", "guardian", "obliteration", "protection"]:
        priceMap[i] = lookup_handler.get_item_data(i).json()[0]['avgPrice'] / 10
    else:
        priceMap[i] = lookup_handler.get_item_data(i).json()[0]['avgPrice']

async def graph_hones(message):
    honing_plotter.plot_honing_historic(honing_calculator.calculate_honing_historic(message))

    title = f"{message.author.name}'s Hones"
    description = 'Historical Cumulative Honing Deviation from Mean'
    color = discord.Colour.green()
    embed = create_embed(title, description, color)
    embed.set_image(url="attachment://plot_honing_historic.png")
    embed.add_field(name="Link to Website", value="http://20.55.0.43")
    file = discord.File("./images/plot_honing_historic.png", filename="plot_honing_historic.png")
    await message.channel.send(file = file, embed=embed)

