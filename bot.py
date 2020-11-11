# bot.py
import os
import re
import random

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

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
    print("Now active in " + str(len(client.guilds)) + " guilds.")
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
        response += "\t- Join role [role name | roll id]: Join a roll based off its name or number (from the list roles command).\n"
        response += "\t- Leave role [role name | roll id]: Leave a roll based off its name or number (from the list roles command).\n"
        response += "\t- Add role [role name]: Create a new roll and automatically join it.\n"
        response += "\t- **Delete role [role name | roll id]**: Delete a roll based off its name or number (from the list roles command). Only the original creator of a roll can delete that roll.\n"
        response += "\t- Pogbot call poll. [poll prompt]: Create a yes / no poll with the given prompt.\n"
        response += "\t- Pogbot stats for nerds: Print out some info about the project, nerdy!\n"
        response += "\nExample commands:\n"
        response += "\t\"Join role 3\"\n"
        response += "\t\"Leave role nsfw\"\n"
        response += "\t\"Pogbot Call Poll. Is fish pog better than normal pog?\"\n"
        response += "\t\"Create role Gamers\"\n"
        response += "\nCommand Aliases:\n"
        response += "\tCreate Role == Add Role\n"
        response += "\n"
        response += "_Commands in bold are planned commands, and are not currently implimented._"

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
    Join role command handling
    '''
    if message.content.lower().startswith("join role"):
        await RoleManager.join_role(message)
 
    '''
    Leave role command handling
    '''
    if message.content.lower().startswith("leave role"):
        await RoleManager.leave_role(message)

    '''
    Create role command handling
    '''
    if message.content.lower().startswith("add role") or message.content.lower().startswith("create role"):
        await RoleManager.add_role(message)
    
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
    if message.content.lower().startswith("pogbot call poll."):
        print("Running a poll.")
        # @here so everyone in the channel gets notified a poll is active
        response = "@here\n"
        # Add the prompt to the poll (without the trigger phrase)
        prompt = re.compile(re.escape("pogbot call poll."), re.IGNORECASE)
        prompt = prompt.sub("", message.content)
        response += prompt + "\n"

        # send the message, and store it so we can add the reactions
        msg = await message.channel.send(response)
        
        # delete the message that sent the poll, so only the poll is shown
        await message.delete()

        # add the reactions:
        # thumbs up
        await msg.add_reaction("👍")
        # thumbs down
        await msg.add_reaction("👎")

    '''
    HIDDEN COMMAND: cloc
    '''
    if message.content.lower() == "pogbot stats for nerds":
        print("Someone is a nerd!")
        await message.channel.send(os.popen("cloc .").read()) 
        await message.channel.send("\n_____\n") 
        await message.channel.send(os.popen("tree .").read()) 

    # add a newline between each log, this should always be the last thing this function does.
    print("-\n")

'''
RoleManager is a singleton.
Private:
    __instance
    __db_path (default is ./.owners)
    __roles_metadata
    __get_roles(message)
    __new__()
Public:
    join_role(message)
    leave_role(message)
    add_role(message)
    delete_role(message)
'''
class RoleManager(object):
    __instance = None
    __db_path = "./.owners"
    __roles_metadata = {}

    def __new__(cls):
        if RoleManager.__instance is None:
            RoleManager.__instance = object.__new__(cls)
        return RoleManager.__instance

    def __get_roles(self, message):
        # get the guild object this message was posted in
        guild = client.get_guild(message.guild.id)
        # get all roles in the guild
        all_roles = guild.roles
        roles = []
    
        # filter out all roles not following restrictions
        for role in all_roles:
            if str(role.color) == "#000000" and role.name != "@everyone":
                roles.append(role.name.lower())
        
        return roles

    async def add_role(message):
        print("Attempting to create a new roll...")
        self = RoleManager()
        user = message.author
        guild = client.get_guild(message.guild.id)
        roles = self.__get_roles(message)
        if message.content.lower().startswith("add"):
            role_parse = message.content.lower().replace("add role ", "")
        else:
            role_parse = message.content.lower().replace("create role ", "")


        print("\tAdding role: " + role_parse)

        # avoid duplicate role names
        if role_parse in roles:
            print("\tRole already exists. Aborting.\nDone.")
            await message.channel.send("A role with the name already exists! I'm not going to let you create duplicate roles.")
            return

        # create the role
        await guild.create_role(name=role_parse)

        # log the owner to a file so only they can delete it later
        owners_file = open(self.__db_path, "a")
        owners_file.write(user.name + " -- " + role_parse)
        owners_file.close()

        # add the user to the new role
        message.content = "join role " +  role_parse
        await RoleManager.join_role(message, silent=True)

        # respond to the user
        await message.channel.send("It's done! I've made the new role \"" + role_parse + "\". Don't worry, I've already added you to this new role. :)")

        print("Done.")
        return

    async def join_role(message, silent=False):
        print("Attempting to add someone to a roll...")
        self = RoleManager()
        user = message.author
        role_parse = message.content.lower().replace("join role ", "")
        using_id = True
        task_completed = False
        roles = self.__get_roles(message)
        
        # detect if the user is adding a role by name or by id
        try:
            role_parse = int(role_parse) - 1
        except ValueError:
            using_id = False

        # if using id
        if using_id:
            # catches invalid ids
            try:
                # get the role name
                selected_role = roles[role_parse] # need try except block here
                print("\tAdding user to roll (by id): " + selected_role)
                # sift through server roles for a match
                for server_role in message.guild.roles:
                    if server_role.name.lower() == selected_role:
                        # add matched role
                        await user.add_roles(server_role)
                response = "You got it boss! I've added you to the \"" + selected_role + "\" roll."
            except IndexError:
                print("\tIndex error. Aborting.")
                response = "I could not find a role with that id, sorry!"
        # if using name
        else:
            # need to make sure the given name is a roll, so look through known roles
            for role in roles:
                # if the given role is a known role
                if role == role_parse:
                    print("\tAdding user to roll: " + role)
                    # sift through the server roles for a match
                    for server_role in message.guild.roles:
                        if server_role.name.lower() == role:
                            # add matched role
                            await user.add_roles(server_role)
                    response = "You got it boss! I've added you to the \"" + role + "\" roll."
                    task_completed = True
            # if the given role is not a known role
            if not task_completed:
                response = "I could not find a role with that name, sorry!"
        if not silent:
            await message.channel.send(response)
        print("Done.")
        return

    async def leave_role(message):
        print("Attempting to remove someone from a roll...")
        self = RoleManager()
        user = message.author
        role_parse = message.content.lower().replace("leave role ", "")
        using_id = True
        task_completed = False
        roles = self.__get_roles(message)
        
        # detect if the user is adding a role by name or by id
        try:
            role_parse = int(role_parse) - 1
        except ValueError:
            using_id = False

        # if using id
        if using_id:
            # catches invalid ids
            try:
                # get the role name
                selected_role = roles[role_parse] # need try except block here
                print("\tRemoving role from user (by id): " + selected_role)
                # sift through server roles for a match
                for server_role in message.guild.roles:
                    if server_role.name.lower() == selected_role:
                        # add matched role
                        await user.remove_roles(server_role)
                response = "Can do! I've removed the role \"" + selected_role + "\" for you."
            except IndexError:
                print("\tIndex error. Aborting.")
                response = "I could not find a role with that id, sorry!"
        # if using name
        else:
            # need to make sure the given name is a roll, so look through known roles
            for role in roles:
                # if the given role is a known role
                if role == role_parse:
                    print("\tRemoving role from user: " + role)
                    # sift through the server roles for a match
                    for server_role in message.guild.roles:
                        if server_role.name.lower() == role:
                            # add matched role
                            await user.remove_roles(server_role)
                    response = "Can do! I've removed the role \"" + selected_role + "\" for you."
                    task_completed = True
            # if the given role is not a known role
            if not task_completed:
                response = "I could not find a role with that name, sorry!"
        await message.channel.send(response)
        print("Done.")
        return



client.run(TOKEN)
