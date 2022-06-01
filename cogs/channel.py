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


class ChannelManager(commands.Cog, name="channelmanager"):
    def __init__(self, bot):
        self.bot = bot

    async def createCategory(category, context):
        """
        [(Required) category name, message context] creates a category and returns category object
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
        [(Required) category name, mesage context] get category and if no category match, create a category. Returns category object.
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
        [(Required) channel name, category name, message context, description] creates channel in category with description and name, returns channel object.
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

    async def createRole(context, rolename: str, permissions: discord.Permissions = discord.Permissions.general(), color=discord.Colour.default()):
        """
        [(Required) message context, role name, (optional) permissions, color] creates a role with default general permissions, with specifed name.
        """
        return await context.guild.create_role(name=rolename, permissions=permissions, colour=color)

    def getRoleSemester():
        dateTest = datetime.date.today()
        month = dateTest.month
        year = dateTest.year
        if month >= 11 or month <= 2:
            semester = 'Winter'
        elif 2 < month <= 7:
            semester = 'Summer'
        else:
            semester = "Fall"
        return (semester, year)

    @ commands.command(name="csvparse")
    @ has_permissions(administrator=True)
    async def csvparse(self, context, filename=None):
        """
        [(Required) filename] parses a csv into class channels and categories.
        """

        channelnames = []
        categories = []
        description = {}
        category_roles = {}

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
                        prof = prof.split()
                        prof_lastname = prof[len(prof)-2]

                    semester, year = ChannelManager.getRoleSemester()

                    # assemble class and category names
                    channelname = classtype + "-" + classnum + "-" + prof_lastname
                    categoryname = classtype + "-" + classnum
                    rolename = classtype + ' ' + classnum + \
                        ' ' + str(semester) + ' ' + str(year)

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
        await context.send("Channels and Roles created successfully")

    @ commands.command(name="deleteAllClasses")
    @ has_permissions(administrator=True)
    async def deleteClasses(self, context):
        """
        [No arguments] Admin Only. Deletes channels and categories with cosc-### or math-###,  case insensitive.
        """
        for channel in context.guild.channels:
            if re.search('COSC-[0-9]{3}', channel.name, flags=re.I):
                await channel.delete()
            elif re.search('MATH-[0-9]{3}', channel.name, flags=re.I):
                await channel.delete()
            elif re.search('STAT-[0-9]{3}', channel.name, flags=re.I):
                await channel.delete()

    @ commands.command(name="deleteAllRoles")
    @ has_permissions(administrator=True)
    async def deleteRoles(self, context):
        for role in context.guild.roles:
            if re.search('COSC [0-9]{3}', role.name, flags=re.I):
                await role.delete()
            elif re.search('MATH [0-9]{3}', role.name, flags=re.I):
                await role.delete()
            elif re.search('STAT [0-9]{3}', role.name, flags=re.I):
                await role.delete()


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(ChannelManager(bot))
