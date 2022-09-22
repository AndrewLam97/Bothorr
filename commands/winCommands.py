from models.Wins import Win
from db_connection import Session
import discord

async def listWins(message):
    with Session() as sess:
        wins = sess.query(Win).filter(Win.discordId == str(message.author.id)).all()
    if len(wins) == 0:
        await message.channel.send("You are a loser with no Ws")
    else:
        descriptions = []
        goldSavedList = []
        for win in wins:
            descriptions.append(win.description)
            goldSavedList.append(str(win.goldSaved))
        embedVar = discord.Embed(title=f"{message.author.name}'s Wins", color=discord.Color.green())
        embedVar.add_field(name="Description", value="\n".join(descriptions), inline=False)
        embedVar.add_field(name="Gold Saved", value="\n".join(goldSavedList), inline=False)
        await message.channel.send(embed=embedVar)

async def addWin(message):
    # Split string by spaces
    # Entry[0] is !W command
    # Entry[-1] is gold saved amount
    # Everything in between is description
    Entry = message.content.split(" ")
    try:
        goldSaved = int(Entry[-1])
    except ValueError:
        await message.channel.send('Not a W')
    newWin = Win(discordId=str(message.author.id), discordUsername=message.author.name, goldSaved=goldSaved, description=" ".join(Entry[1:-1]))
    with Session() as sess:
        sess.add(newWin)
        sess.commit()
    await message.channel.send('fk matteo')