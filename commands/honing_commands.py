import discord

from util.embeds import create_embed
from util.honing import honing_calculator, honing_plotter


async def graph_hones(message):
    honing_plotter.plot_honing_historic(honing_calculator.calculate_honing_historic(message))

    title = f"{message.author.name}'s Hones"
    description = 'Historical Cumulative Honing Deviation from Mean'
    color = discord.Colour.green()
    embed = create_embed(title, description, color)
    embed.set_image(url="attachment://plot_honing_historic.png")
    file = discord.File("./images/plot_honing_historic.png", filename="plot_honing_historic.png")
    await message.channel.send(file = file, embed=embed)

