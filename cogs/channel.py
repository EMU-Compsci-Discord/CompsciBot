import os
import sys
import csv
import yaml
from discord.ext import commands
from discord.ext.commands import has_permissions
import re

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Here we name the cog and create a new class for the cog.
testGuild = 931309621027684413


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

        try:
            return await guild.create_category(category)
        except:
            print("Issue with ", category, ".  Error: ", sys.exc_info()[0])

    def makeDict(categories, channels):
        classDict = {}
        for channel in channels:
            for category in categories:
                if (category in channel):
                    classDict[channel] = category
        print(classDict)
        return classDict

    @commands.command(name="channelparse")
    @has_permissions(administrator=True)
    async def channelparse(self, context):
        """
        [Optional filename argument] This command sets up channels from a csv
        """

        channelnames = []
        categories = []

        # parses command to get message content
        prefix = config["bot_prefix"]
        startLen = len(prefix) + len("channelparse")
        filename = context.message.content[startLen:].strip()

        if(re.search("\W", filename)):
            await context.send("Please input a filename without special characters or extensions")
            return

        filename = "resources\\"+filename+".csv"
        print("filename: ", filename)

        # read and parse the csv
        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:

                # check if those attributes exist
                if(row[2].strip() and row[3].strip() and row[19].strip()):

                    classtype = row[2]
                    # first 3 numbers only (not L1,L2,L3)
                    classnum = row[3][0:3]
                    prof = row[19]

                    if (prof != "TBA"):
                        prof = prof.split()[1]

                    # assemble class and category names
                    channelname = classtype+"-"+classnum+"-"+prof
                    categoryname = classtype + "-"+classnum

                    if(categoryname not in categories):
                        categories.append(categoryname)

                    channelnames.append(channelname)
            classDict = ChannelManager.makeDict(categories, channelnames)
            # unable to creat channels
            for channel in channelnames:
                if('388' in channel or '571' in channel or '511' in channel):
                    continue
                await ChannelManager.createChannel(channel, classDict[channel], context)

        await context.send("Channels Created Successfully")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.


def setup(bot):
    bot.add_cog(ChannelManager(bot))
