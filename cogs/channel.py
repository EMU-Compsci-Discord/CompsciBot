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

    async def create_role(context, role_name: str, permissions: discord.Permissions = discord.Permissions.none(), color=discord.Colour.default()):
        """
        [(Required) message context, role name, (optional) permissions, color] creates a role with specified permissions, with specifed name.
        """
        return await context.guild.create_role(name=role_name, permissions=permissions, colour=color)

    def get_role_semester():
        today = datetime.date.today()
        month = today.month
        year = today.year
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

        if filename is None:
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
                    classnum = row[course_number][0:3]
                    prof = row[professor]

                    if classnum in class_blacklist or classnum[0] == "5":
                        continue

                    if prof != "TBA":
                        prof_parts = prof.split()
                        prof_lastname = prof_parts[-2]

                        # deals with suffixes
                        if prof_lastname.lower() in ['sr', 'jr', 'ii', 'iii', 'iv']:
                            prof_lastname = prof_parts[-3]

                    # assemble class and category names
                    channel_name = f"{class_type}-{classnum}-{prof_lastname}"
                    category_name = f"{class_type}-{classnum}"

                    if row[days].strip() != "" or row[times].strip() != "":
                        description = f"{row[days].strip()} {row[times].strip()}"
                    else:
                        description = "No time listed"

                    category_names.add(category_name)

                    await ChannelManager.create_channel(channel_name, category_name, context, description)

        # make a mod role to see all classes
        mod_class_role = find(lambda role: role.name == 'All Classes', context.guild.roles)
        if mod_class_role is None:
            mod_class_role = await ChannelManager.create_role(context, 'All Classes', color=discord.Colour.blue())

        for category_name in category_names:
            role_name = f"{category_name.replace('-', ' ')} {semester} {year}"
            category_object = await ChannelManager.get_category(category_name, context)
            category_role = await ChannelManager.create_role(context, role_name, color=discord.Colour.blue())
            # gives basic permissions to a role for its assigned channel
            await category_object.set_permissions(
                category_role,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                read_message_history=True)
            await category_object.set_permissions(
                mod_class_role,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                read_message_history=True)

        await context.send("Channels and Roles created successfully")

    @commands.command(name="deleteclasses")
    @has_permissions(administrator=True)
    async def delete_classes(self, context):
        """
        [No arguments] Admin Only. Deletes channels and categories with COSC-###, MATH-###, or STAT-### (case insensitive).
        """
        for channel in context.guild.channels:
            if re.search('(COSC|MATH|STAT)-[0-9]{3}', channel.name, flags=re.I):
                await channel.delete()

    @commands.command(name="deleteclassroles")
    @has_permissions(administrator=True)
    async def delete_roles(self, context):
        """
        [No arguments] Admin Only. Deletes roles with COSC-###, MATH-###, or STAT-### (case insensitive).
        """
        for role in context.guild.roles:
            if re.search('(COSC|MATH|STAT) [0-9]{3}', role.name, flags=re.I):
                await role.delete()



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(ChannelManager(bot))
