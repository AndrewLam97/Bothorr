import discord

from util.embeds import create_embed
from util.honing import honing_plotter
from util.honing.honing_data_manipulator import HoningDataManipulator


async def graph_hones(message, honingDataManipulator: HoningDataManipulator):
    honing_plotter.plot_honing_historic(honingDataManipulator.calculate_honing_historic(message))

    title = f"{message.author.name}'s Hones"
    description = 'Historical Cumulative Honing Deviation from Mean'
    color = discord.Colour.green()
    embed = create_embed(title, description, color)
    embed.set_image(url="attachment://plot_honing_historic.png")
    embed.add_field(name="Link to Website", value="http://20.55.0.43")
    file = discord.File("./images/plot_honing_historic.png", filename="plot_honing_historic.png")
    await message.channel.send(file = file, embed=embed)

