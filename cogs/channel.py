import sys
import csv
import yaml
from nextcord.ext.commands import Cog
from nextcord.ext.application_checks import has_permissions
from nextcord.utils import find
import datetime
import re
import nextcord
from nextcord import Interaction, SlashOption, PermissionOverwrite, Permissions, Colour


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


class ChannelManager(Cog, name="channelmanager"):
    def __init__(self, bot):
        self.bot = bot

    async def create_category(category_name, interaction: Interaction):
        """
        creates a category and returns category object
        """

        guild = interaction.guild
        overwrites = {
            guild.default_role: PermissionOverwrite(read_messages=False)
        }
        try:
            return await guild.create_category(category_name, overwrites=overwrites)
        except:
            print("Issue with ", category_name, ".  Error: ", sys.exc_info()[0])

    async def get_category(category_name, interaction: Interaction):
        """
        get category and if no category match, create a category. Returns category object.
        """
        guild = interaction.guild

        # get category by category name
        category = find(lambda category: category.name == category_name, guild.categories)
        if(category is None):
            category = await ChannelManager.create_category(category_name, interaction)
        return category

    async def create_channel(channel_name: str, category_name: str, interaction: Interaction, description: str):
        """
        creates channel in category with description and name, returns channel object.
        """
        guild = interaction.guild

        category = await ChannelManager.get_category(category_name, interaction)

        return await guild.create_text_channel(channel_name, category=category, topic=description)

    async def create_role(interaction: Interaction, role_name: str, permissions: Permissions = Permissions.none(), color=Colour.default()):
        """
        creates a role with specified permissions, with specifed name.
        """
        return await interaction.guild.create_role(name=role_name, permissions=permissions, colour=color)

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

    @nextcord.slash_command(name="csvparse", description="Parse a csv file and create channels and roles for each class.")
    @has_permissions(administrator=True)
    async def csvparse(self, interaction: Interaction, filename: str = SlashOption(description="The name of the csv file to parse.", required=True)):
        if re.search("^[a-zA-Z0-9_\-]+\.csv$", filename) is None:
            await interaction.response.send_message("Please input a .csv filename without special characters or extensions.")
            return

        await interaction.response.defer()

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

                    await ChannelManager.create_channel(channel_name, category_name, interaction, description)

        # make a mod role to see all classes
        mod_class_role = find(lambda role: role.name == 'All Classes', interaction.guild.roles)
        if mod_class_role is None:
            mod_class_role = await ChannelManager.create_role(interaction, 'All Classes', color=nextcord.Colour.blue())

        for category_name in category_names:
            role_name = f"{category_name.replace('-', ' ')} {semester} {year}"
            category_object = await ChannelManager.get_category(category_name, interaction)
            category_role = await ChannelManager.create_role(interaction, role_name, color=nextcord.Colour.blue())
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

        await interaction.followup.send("Channels and Roles created successfully")

    @nextcord.slash_command(name="deleteclasses", description="Admin Only. Deletes channels, categories, and roles with course names in them.")
    @has_permissions(administrator=True)
    async def delete_classes(self, interaction: Interaction):
        await interaction.response.defer()

        count_channels = 0
        for channel in interaction.guild.channels:
            if re.search('(COSC|MATH|STAT)-[0-9]{3}', channel.name, flags=re.I):
                await channel.delete()
                count_channels += 1

        count_roles = 0
        for role in interaction.guild.roles:
            if re.search('(COSC|MATH|STAT) [0-9]{3}', role.name, flags=re.I):
                await role.delete()
                count_roles += 1

        await interaction.followup.send(f"Deleted {count_channels} channels and categories and {count_roles} roles.")



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(ChannelManager(bot))
