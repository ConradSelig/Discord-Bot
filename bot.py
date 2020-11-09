# bot.py
import os
import random

import discord
from discord.ext.commands import Bot
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='you ʕ•ᴥ•ʔ'))
    print("Connected.")
    print("Guilds:", client.guilds)
    print("\n==============================\n")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == 'pog' or message.content == "Pog":
        pog_images = os.listdir("./Pog_Images/")
        index = random.randint(0, len(pog_images) - 1)
        
        print("Pogging! " + str(index))
        await message.channel.send(file=discord.File("./Pog_Images/" + pog_images[index]))

    if message.content == "pog count":
        await message.channel.send("I currently know " + str(len(os.listdir("./Pog_Images/"))) + " different ways to Pog.")

    if message.content == "list roles":
        guild = client.get_guild(message.guild.id)
        all_roles = guild.roles
        roles = []

        for role in all_roles:
            if str(role.color) == "#000000" and role.name != "@everyone":
                roles.append(role)

        response = "";
        
        if len(roles) == 0:
            response = "This server has no general roles."
        elif len(roles) == 1:
            response += guild.name + " only has 1 role.\n"
            for i, role in enumerate(roles):
                response += "\t" + str(i+1) + ". " + role.name + "\n"
        else:
            response += guild.name + " currently has " + str(len(roles)) + " roles.\n"
            for i, role in enumerate(roles):
                response += "\t" + str(i+1) + ". " + role.name + "\n"

        print("Printing roles. (" + str(len(roles)) + " roles printed)")
        await message.channel.send(response)

client.run(TOKEN)
