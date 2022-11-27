import discord


#Singular Embed Base
def create_embed(title, description, color, type = 'rich'):
    return discord.Embed(type = type, title = title, description = description,color = color)