import os
import sys
import csv
import yaml
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import find
import datetime
import re

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# csv column names
department = 2  # example: COSC
course_number = 3  # example: 101
days = 8  # example: WM
times = 9  # 09:00 am-12:50 pm
professor = 19  # example: Zenia Christine Bahorski (P)

# classes we do not want to create channels for
class_blacklist = ['106', '146', '388']


class ChannelManager(commands.Cog, name="channelmanager"):
    def __init__(self, bot):
        self.bot = bot

    async def create_category(category, context):
        """
        [(Required) category name, message context] creates a category and returns category object
        """

        guild = context.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        try:
            return await guild.create_category(category, overwrites=overwrites)
        except:
            print("Issue with ", category, ".  Error: ", sys.exc_info()[0])

    async def get_category(category_name, context):
        """
        [(Required) category name, mesage context] get category and if no category match, create a category. Returns category object.
        """
        guild = context.guild

        # get category by category name
        category = find(lambda category: category.name == category_name, guild.categories)
        if(category is None):
            category = await ChannelManager.create_category(category_name, context)
        return category

    async def create_channel(channel_name: str, category_name: str, context, description: str):
        """
        [(Required) channel name, category name, message context, description] creates channel in category with description and name, returns channel object.
        """
        guild = context.guild

        category = await ChannelManager.get_category(category_name, context)

        return await guild.create_text_channel(channel_name, category=category, topic=description)

    def makeDict(categories, channels):
        classDict = {}
        for channel in channels:
            for category in categories:
                if (category in channel):
                    classDict[channel] = category
        return classDict

    @ commands.command(name="channelparse")
    @ has_permissions(administrator=True)
    async def channelparse(self, context, filename=None):
        """
        [(Required) filename] parses a csv into class channels and categories.
        """

        channelnames = []
        categories = []
        description = {}

        if (filename is None):
            await context.send("Please specify a .csv file as an argument.")

        if re.search("^[a-zA-Z0-9_\-]+\.csv$", filename) is None:
            await context.send("Please input a .csv filename without special characters or extensions.")
            return

        category_names = set()

        filename = "./resources/" + filename

        # read and parse the csv
        with open(filename) as csv_file:
            semester, year = ChannelManager.get_role_semester()

            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:

                # check if those attributes exist
                if row[department].strip() != "" and row[course_number].strip() != "" and row[professor].strip() != "":

                    class_type = row[department]

                    # first 3 numbers only (not L1,L2,L3)
                    classnum = class_info[3][0:3]
                    prof = class_info[19]

                    if (prof != "TBA"):
                        prof = prof.split()
                        prof_lastname = prof[len(prof)-2]

                    # assemble class and category names
                    channelname = classtype+"-"+classnum+"-"+prof_lastname
                    categoryname = classtype + "-"+classnum

                    if(class_info[8].strip() or class_info[9].strip()):
                        description[channelname] = class_info[8].strip() + \
                            " " + class_info[9].strip()
                    else:
                        description[channelname] = "No time listed"

                    if(categoryname not in categories):
                        categories.append(categoryname)
                        # create role and save returned Role Object in dict
                        category_roles[categoryname] = await ChannelManager.createRole(
                            context, rolename, color=discord.Colour.blue())

                    channelnames.append(channelname)

            classDict = ChannelManager.makeDict(categories, channelnames)

            for channel in channelnames:
                if('388' in channel or '571' in channel or '511' in channel):
                    continue
                await ChannelManager.createChannel(channel, classDict[channel], context, description[channel])

            for category in categories:
                category_object = await ChannelManager.getCategory(category, context)
                # gives basic permissions to a role for its assigned channel
                await category_object.set_permissions(
                    category_roles[category],
                    read_messages=True,
                    send_messages=True,
                    add_reactions=True,
                    read_message_history=True)
                await category_object.set_permissions(
                    modClassRole,
                    read_messages=True,
                    send_messages=True,
                    add_reactions=True,
                    read_message_history=True)
        await context.send("Channels and Roles created successfully")

    @ commands.command(name="deleteAllClasses")
    @ has_permissions(administrator=True)
    async def deleteAll(self, context):
        """
        [No arguments] Admin Only. Deletes channels and categories with COSC-###, MATH-###, or STAT-### (case insensitive).
        """
        for channel in context.guild.channels:
            if re.search('COSC-[0-9]{3}', channel.name) or re.search('cosc-[0-9]{3}', channel.name):
                await channel.delete()
            if re.search('MATH-[0-9]{3}', channel.name) or re.search('math-[0-9]{3}', channel.name):
                await channel.delete()
            if re.search('STAT-[0-9]{3}', channel.name) or re.search('stat-[0-9]{3}', channel.name):
                await channel.delete()


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(ChannelManager(bot))
