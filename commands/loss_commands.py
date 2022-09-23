from models.losses import Loss
from db_connection import Session
import discord

async def list_losses(message):
    with Session() as sess:
        losses = sess.query(Loss).filter(Loss.discordId == str(message.author.id)).all()
    if len(losses) == 0:
        await message.channel.send("No L's - Matteo looking ass")
    else:
        descriptions = []
        goldLostList = []
        totalGoldLost = 0
        for loss in losses:
            descriptions.append(loss.description)
            goldLostList.append(str(loss.goldLost))
            totalGoldLost+=loss.goldLost
        embedVar = discord.Embed(title=f"{message.author.name}'s Losses", color=discord.Color.red())
        embedVar.add_field(name="Description", value="\n".join(descriptions))
        embedVar.add_field(name="Gold Lost", value="\n".join(goldLostList))
        embedVar.add_field(name="Total Gold Lost", value=str(totalGoldLost), inline=False)
        await message.channel.send(embed=embedVar)

async def add_loss(message):
    # Split string by spaces
    # Entry[0] is !W command
    # Entry[-1] is gold saved amount
    # Everything in between is description
    Entry = message.content.split(" ")
    try:
        goldLost = int(Entry[-1])
    except ValueError:
        await message.channel.send('Not a L')
    newLoss = Loss(discordId=str(message.author.id), discordUsername=message.author.name, goldLost=goldLost, description=" ".join(Entry[1:-1]))
    with Session() as sess:
        sess.add(newLoss)
        sess.commit()
    await message.channel.send('fk matteo')

async def clear_losses(message):
    with Session() as sess:
        sess.query(Loss).filter(Loss.discordId == str(message.author.id)).delete(synchronize_session = False)
        sess.commit()
    await message.channel.send(message.author.name + "'s losses cleared!")