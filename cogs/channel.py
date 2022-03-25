import os
import sys
import csv
from attr import get_run_validators
import yaml
from discord.ext import commands

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Here we name the cog and create a new class for the cog.
testGuild = 931309621027684413


class Channel(commands.Cog, name="channel"):
    def __init__(self, bot):
        self.bot = bot

    async def createCategory(category, context):
        guild = context.guild
        try:
            return await guild.create_category(category)
        except:
            print("Issue with ", category, ".  Error: ", sys.exc_info()[0])
    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    def makeDict(categories, channels):
        classDict = {}
        for channel in channels:
            for category in categories:
                if (category in channel):
                    classDict[channel] = category
        print(classDict)
        return classDict

    @commands.command(name="channelparse")
    async def channelparse(self, context):
        """
        [Optional filename argument] This command sets up channels from a csv
        """

        channelnames = []
        categories = []
        categoryIds = []
        prefix = config["bot_prefix"]
        startLen = len(prefix) + len("channelparse")
        filename = context.message.content[startLen:].strip()

        if (not filename.strip()):
            filename = 'testcsv.csv'

        print("filename: ", filename)

        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                if(row[2].strip() and row[3].strip() and row[19].strip()):

                    classtype = row[2]
                    # first 3 numbers only (not L1,L2,L3)
                    classnum = row[3][0:3]
                    prof = row[19]

                    if (prof != "TBA"):
                        prof = prof.split()[1]

                    channelname = classtype+"-"+classnum+"-"+prof
                    categoryname = classtype + "-"+classnum

                    if(categoryname not in categories):
                        categories.append(categoryname)

                    channelnames.append(channelname)

            # unable to creat channels
            for channel in channelnames:
                if('388' in channel or '571' in channel or '511' in channel):
                    continue
                await Channel.createChannel(channel, classDict[channel], context)
        # print(channelnames)
        # print(categories)
        await context.send("Test Done")


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Channel(bot))
