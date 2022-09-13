from pathlib import Path
import sys
import csv
from typing import TypedDict
import json
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


# classes we do not want to create channels for
course_blacklist = ['106', '146', '388']


class Section(TypedDict):

    subject: str
    """`COSC`, `STAT`, `MATH`"""

    course: str
    """`111`, `211`, `341W`, `388L4`"""

    days: str
    """`MW`, `TR`, `T`"""

    time: str
    """`09:00 am-10:50 am`, `11:00 am-12:50 pm`"""

    instructor: str
    """`Suchindran Maniccam (P)`, `Philip Lynn Francis III (P)`"""


class SectionJson(TypedDict):

    term: str
    """`Fall 2022`, `Summer 2017`, `Winter 2020-COVID Term Impact`"""

    timestamp: int
    """milliseconds since 1970 """

    classes: list[Section]


JSON_SCHEMA = "https://raw.githubusercontent.com/EMU-Compsci-Discord/compsci-class-scraper/main/json-schema/output-v1.schema.json"


def read_class_json(file_name: str) -> SectionJson:
    if not file_name.endswith('.json'):
        raise Exception("File name must end with .json")

    if re.search("^[a-zA-Z0-9_\-]+\.json$", file_name) is None:
        raise Exception("File name can only contain letters, numbers, dashes and underscores")

    file_path = Path("resources", file_name)

    if not file_path.is_file():
        raise Exception(f"File {file_path} does not exist")

    with open(file_path) as file:
        data = json.load(file)

        if data["$schema"] != JSON_SCHEMA:
            raise Exception(f"Incorrect JSON schema\nExpected: {JSON_SCHEMA}\nFound: {data['$schema']}")

        return data


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
        if (category is None):
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

    @nextcord.slash_command(name="importclasses", description="Import a JSON file and create channels and roles for each class.")
    @has_permissions(administrator=True)
    async def import_classes(self, interaction: Interaction, file_name: str = SlashOption(description="The name of the JSON file to parse.", required=True)):
        try:
            json = read_class_json(file_name)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            return

        await interaction.response.defer()

        channels_count = 0
        roles_count = 0

        category_names: set[str] = set()

        for section in json["classes"]:

            # first 3 numbers only (not L1,L2,L3)
            course_number = section["course"][0:3]
            professor = section["instructor"]

            if course_number in course_blacklist or course_number[0] == "5":
                continue

            if professor != "TBA":
                prof_parts = professor.split()
                prof_lastname = prof_parts[-2]

                # deals with suffixes
                if prof_lastname.lower() in ['sr', 'jr', 'ii', 'iii', 'iv']:
                    prof_lastname = prof_parts[-3]

            # assemble class and category names
            channel_name = f"{section['subject']}-{course_number}-{prof_lastname}"
            category_name = f"{section['subject']}-{course_number}"

            if section["days"] != "" or section["time"] != "":
                description = f"{section['days']} {section['time']}"
            else:
                description = "No time listed"

            category_names.add(category_name)

            await ChannelManager.create_channel(channel_name, category_name, interaction, description)
            channels_count += 1

        # make a mod role to see all classes
        mod_class_role = find(lambda role: role.name == 'All Classes', interaction.guild.roles)
        if mod_class_role is None:
            mod_class_role = await ChannelManager.create_role(interaction, 'All Classes', color=nextcord.Colour.blue())
            roles_count += 1

        for category_name in category_names:
            role_name = f"{category_name.replace('-', ' ')} {json['term']}"
            category_object = await ChannelManager.get_category(category_name, interaction)
            category_role = await ChannelManager.create_role(interaction, role_name, color=nextcord.Colour.blue())
            roles_count += 1
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

        await interaction.followup.send(f"Created {channels_count} channels and {roles_count} roles.")

    @nextcord.slash_command(name="deleteclasses", description="Admin Only. Deletes channels, categories, and roles with course names in them.")
    @has_permissions(administrator=True)
    async def delete_classes(self, interaction: Interaction):
        await interaction.response.defer()

        channels_count = 0
        roles_count = 0

        for channel in interaction.guild.channels:
            if re.search('(COSC|MATH|STAT)-[0-9]{3}', channel.name, flags=re.I):
                await channel.delete()
                channels_count += 1

        for role in interaction.guild.roles:
            if re.search('(COSC|MATH|STAT) [0-9]{3}', role.name, flags=re.I):
                await role.delete()
                roles_count += 1

        await interaction.followup.send(f"Deleted {channels_count} channels and categories and {roles_count} roles.")


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(ChannelManager(bot))
