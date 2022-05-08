import os
import sys
import csv
import yaml
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import find
import re

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


class ChannelManager(commands.Cog, name="channelmanager"):
    def __init__(self, bot):
        self.bot = bot

    async def createCategory(category, context):
        """
        creates a category

            Parameters:
                category: the name of the category
                context: the context of the command

            Returns:
                the category object
        """

        guild = context.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False)
        }
        try:
            return await guild.create_category(category, overwrites=overwrites)
        except:
            print("Issue with ", category, ".  Error: ", sys.exc_info()[0])

    async def getCategory(category_name, context):
        """
        Finds a category by same or if none exists creates a new one
            Parameters:
                category: the name of the category
                context: the context of the command

            Returns:
                the category object
        """
        guild = context.guild

        # get category by category name
        category = find(lambda category: category.name ==
                        category_name, guild.categories)
        if(category == None):
            category = await ChannelManager.createCategory(category_name, context)
        return category

    async def createChannel(channel_name: str, category_name: str, context, description: str):
        """
        Given a channel and a category name, creates a channel and assigns it to the category.
            Parameters:
                channel_name: the name of the channel
                category_name: the name of the category
            Returns: 
                the channle object
        """
        guild = context.guild

        category = await ChannelManager.getCategory(category_name, context)

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
        This command sets up organized categories and channels from a specified csv, with default private permissions.
        Only Administrators can call this command. 
            Parameters:
                filename: a csv file ending in .csv consisting of letters, numbers, hyphens or underscores
        """

        channelnames = []
        categories = []

        if (filename is None):
            await context.send("Please specify a .csv file as an argument.")

        if(not re.search("^[a-zA-Z0-9_\-]+\.csv$", filename)):
            await context.send("Please input a .csv filename without special characters or extensions")
            return

        filename = "./resources/"+filename

        # read and parse the csv
        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for class_info in csvreader:

                # check if those attributes exist
                if(class_info[2].strip() and class_info[3].strip() and class_info[19].strip()):

                    classtype = class_info[2]

                    # first 3 numbers only (not L1,L2,L3)
                    classnum = class_info[3][0:3]
                    prof = class_info[19]

                    if (prof != "TBA"):
                        prof = prof.split()[1]

                    # assemble class and category names
                    channelname = classtype+"-"+classnum+"-"+prof
                    categoryname = classtype + "-"+classnum
                    description = ''

                    if(class_info[8].strip() or class_info[9].strip()):
                        decription = class_info[8].strip(
                        )+" " + class_info[9].strip()

                    if(categoryname not in categories):
                        categories.append(categoryname)

                    channelnames.append(channelname)

            classDict = ChannelManager.makeDict(categories, channelnames)

            # unable to create channels
            for channel in channelnames:
                if('388' in channel or '571' in channel or '511' in channel):
                    continue
                await ChannelManager.createChannel(channel, classDict[channel], context, description)

        await context.send("Channels Created Successfully")

    @ commands.command(name="deleteAllCOSC")
    @ has_permissions(administrator=True)
    async def deleteAll(self, context):
        """
        Deletes channels and categories with cosc### or COSC### in a server. Must have admin permissions to execute.
        """
        for channel in context.guild.channels:
            if re.search('COSC-[0-9]{3}', channel.name) or re.search('cosc-[0-9]{3}', channel.name):
                await channel.delete()


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.


def setup(bot):
    bot.add_cog(ChannelManager(bot))
