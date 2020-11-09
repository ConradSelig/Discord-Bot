# bot.py
import os
import random

import discord
from discord.ext.commands import Bot
from discord.ext import commands

from dotenv import load_dotenv
from urllib.parse import urlparse

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

    channel = message.channel
    category = channel.category

    '''
    Print the help text
    '''
    if message.content.lower() == "pogbot help":
        padding = 60
        response = "You're using Pogbot version " + os.getenv('VERSION') + ". Pog!\n\n"
        response += "Commands in this version:\n"
        response += "\t- Pogbot help: Display this text.\n"
        response += "\t- Pog: Reply to someone saying \"pog\" with a random image of a pog.\n"
        response += "\t- Pog count: Print the number of ways I currently know how to reply to the Pog command\n"
        response += "\t- List roles: Display roles available to join.\n"
        response += "\t- **Join role [role name | roll id]**: Join a roll based off its name or number (from the list roles command).\n"
        response += "\t- **Leave role [role name | roll id]**: Leave a roll based off its name or number (from the list roles command).\n"
        response += "\t- **Add role [role name]**: Create a new roll and automatically join it.\n"
        response += "\t- **Delete role [role name | roll id]**: Delete a roll based off its name or number (from the list roles command). Only the original creator of a roll can delete that roll.\n"
        response += "\t- Pogbot call poll. [poll prompt]: Create a yes / no poll with the given prompt.\n"
        response += "\n_Commands in bold are planned commands, and are not currently implimented._"

        print("Displaying help text.")
        await message.channel.send(response)

    '''
    Post a pog image to pog messages. An image is only posted if the only text in the image is "pog" (lowered)
    '''
    if message.content.lower() == 'pog':
        # get a list of all possible images
        pog_images = os.listdir("./Pog_Images/")
        # get a random index in the list
        index = random.randint(0, len(pog_images) - 1)
        
        print("Pogging! " + str(index))
        # post the random image
        await message.channel.send(file=discord.File("./Pog_Images/" + pog_images[index]))

    '''
    Print how many different pog reactions there are
    '''
    if message.content.lower() == "pog count":
        await message.channel.send("I currently know " + str(len(os.listdir("./Pog_Images/"))) + " different ways to Pog.")

    '''
    List available roles for joining. A roll must be compliant with the following restrictions to show up in the list:
        1. Not be @everyone
        2. Have a color of #000000 (default color)
    '''
    if message.content == "list roles":
        # get the guild object this message was posted in
        guild = client.get_guild(message.guild.id)
        # get all roles in the guild
        all_roles = guild.roles
        roles = []

        # filter out all roles not following restrictions
        for role in all_roles:
            if str(role.color) == "#000000" and role.name != "@everyone":
                roles.append(role)

        response = "";
        
        # if block formats text based off how many available roles there are
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
        # reply with the list of roles
        await message.channel.send(response)

    '''
    Meme reactions. Adds a thumbs up and a thumbs down to posted memes. 
    Only adds reactions to messages compliant with the following restrictions:
        1. Message must be in a channel that is in a category with "memes" in the name -OR-
        1b. The channel name itself must be "memes" (lowered)
        2. Message must have an image attached -OR-
        2b. Message must be a url link with no other text.
    '''
    if "memes" == channel.name.lower() or "memes" in category.name.lower():
        print("Possible meme detected...")
        # create a parse object to detect if the message is a url
        url_parse = urlparse(message.content)
        # evaluate the parse result
        is_url = url_parse.scheme != "" and url_parse.netloc != ""
        # if the message follows the restrictions
        if len(message.attachments) == 1 or is_url:
            print("\tAdding rating reactions.")
            # add the reactions:
            # thumbs up
            await message.add_reaction("👍")
            # thumbs down
            await message.add_reaction("👎")
        print("\tDone.")

    '''
    Poll setup. This will be for just yes / no polls. Only looks for messages that start with "Pogbot call poll."
    '''
    if message.content.startswith("Pogbot call poll."):
        # @here so everyone in the channel gets notified a poll is active
        response = "@here\n"
        # Add the prompt to the poll (without the trigger phrase)
        response += message.content.replace("Pogbot call poll.","")

        # send the message, and store it so we can add the reactions
        msg = await message.channel.send(response)
        
        # delete the message that sent the poll, so only the poll is shown
        await message.delete()

        # add the reactions:
        # thumbs up
        await msg.add_reaction("👍")
        # thumbs down
        await msg.add_reaction("👎")


client.run(TOKEN)
