import asyncio
from collections import OrderedDict
from pathlib import Path
import sys
from typing import Coroutine, TypedDict
import json
import yaml
from nextcord.ext.commands import Cog
from nextcord.ext.application_checks import has_permissions
from nextcord.utils import find
import re
import nextcord
from nextcord import Interaction, SlashOption, PermissionOverwrite, Permissions, Colour


with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


# classes we do not want to create channels for
course_blacklist = ['106', '146', '388']


class Section(TypedDict):
    """
    A section of a course imported from JSON
    """

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
    """
    The JSON imported from a file
    """

    term: str
    """`Fall 2022`, `Summer 2017`, `Winter 2020-COVID Term Impact`"""

    timestamp: int
    """milliseconds since 1970 """

    classes: list[Section]


JSON_SCHEMA = "https://raw.githubusercontent.com/EMU-Compsci-Discord/compsci-class-scraper/main/json-schema/output-v1.schema.json"


def read_class_json(file_name: str) -> SectionJson:
    """
    reads a json file containing classes
    """

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


async def create_channel(channel_name: str, category: nextcord.CategoryChannel, interaction: Interaction, description: str):
    """
    creates channel in category with description and name, returns channel object.
    """

    return await interaction.guild.create_text_channel(channel_name, category=category, topic=description)


async def create_role(interaction: Interaction, role_name: str, permissions: Permissions = Permissions.none(), color=Colour.default()):
    """
    creates a role with specified permissions, with specifed name.
    """

    return await interaction.guild.create_role(name=role_name, permissions=permissions, colour=color)


async def create_role_for_category(interaction: Interaction, category: nextcord.CategoryChannel, term: str):
    role_name = f"{category.name.replace('-', ' ')} {term}"
    role = await create_role(interaction, role_name)
    # gives basic permissions to a role for its assigned channel
    await category.set_permissions(
        role,
        read_messages=True,
        send_messages=True,
        add_reactions=True,
        read_message_history=True
    )
    return role


class ChannelManager(Cog, name="channelmanager"):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="importclasses")
    @has_permissions(administrator=True)
    async def import_classes(self, interaction: Interaction, file_name: str = SlashOption(description="The name of the JSON file to parse.", required=True)):
        """
        Import a JSON file and create channels and roles for each class.
        """

        try:
            json = read_class_json(file_name)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            return

        await interaction.response.defer()

        categories_count = 0
        channels_count = 0
        roles_count = 0

        courses_by_category_name: OrderedDict[str, list[Section]] = OrderedDict()

        for section in json["classes"]:

            # first 3 numbers only (not L1,L2,L3)
            course_number = section["course"][0:3]

            if course_number in course_blacklist or course_number[0] == "5":
                continue

            category_name = f"{section['subject']}-{course_number}"

            courses_by_category_name.setdefault(category_name, []).append(section)

        category_coroutine_by_category_name: dict[str, Coroutine[None, None, nextcord.CategoryChannel]] = {}

        for category_name in courses_by_category_name:
            category_coroutine_by_category_name[category_name] = create_category(category_name, interaction)
            categories_count += 1

        # make a mod role to see all classes
        mod_class_role = find(lambda role: role.name == 'All Classes', interaction.guild.roles)
        if mod_class_role is None:
            mod_class_role = await create_role(interaction, 'All Classes', color=nextcord.Colour.blue())
            roles_count += 1

        coroutines = []

        for category_name in courses_by_category_name:
            category = await category_coroutine_by_category_name[category_name]

            for section in courses_by_category_name[category_name]:

                professor = section["instructor"]

                if professor != "TBA":
                    prof_parts = professor.split()
                    prof_lastname = prof_parts[-2]

                    # deals with suffixes
                    if prof_lastname.lower() in ['sr', 'jr', 'ii', 'iii', 'iv']:
                        prof_lastname = prof_parts[-3]

                # assemble class and category names
                channel_name = f"{category_name}-{prof_lastname}"

                if section["days"] != "" or section["time"] != "":
                    description = f"{section['days']} {section['time']}"
                else:
                    description = "No time listed"

                coroutines.append(create_channel(channel_name, category, interaction, description))
                channels_count += 1

            coroutines.append(create_role_for_category(interaction, category, json["term"]))
            roles_count += 1

            coroutines.append(
                category.set_permissions(
                    mod_class_role,
                    read_messages=True,
                    send_messages=True,
                    add_reactions=True,
                    read_message_history=True
                )
            )

        await asyncio.gather(*coroutines)

        await interaction.followup.send(f"Created {channels_count} channels, {categories_count} categories, and {roles_count} roles.")

    @nextcord.slash_command(name="deleteclasses")
    @has_permissions(administrator=True)
    async def delete_classes(self, interaction: Interaction):
        """
        Admin Only. Deletes channels, categories, and roles with course names in them.
        """

        await interaction.response.defer()

        channels_count = 0
        roles_count = 0

        coroutines = []

        for channel in interaction.guild.channels:
            if re.search('(COSC|MATH|STAT)-[0-9]{3}', channel.name, flags=re.I):
                coroutines.append(channel.delete())
                channels_count += 1

        for role in interaction.guild.roles:
            if re.search('(COSC|MATH|STAT) [0-9]{3}', role.name, flags=re.I):
                coroutines.append(role.delete())
                roles_count += 1

        await asyncio.gather(*coroutines)

        await interaction.followup.send(f"Deleted {channels_count} channels and categories and {roles_count} roles.")


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(ChannelManager(bot))
