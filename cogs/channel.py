import asyncio
from collections import OrderedDict
from pathlib import Path
from string import ascii_lowercase
import sys
from typing import Coroutine, TypedDict, Generator
import json
import yaml
import logging
from nextcord.ext.commands import Cog
from nextcord.ext.application_checks import has_permissions
from nextcord.utils import find
import re
import nextcord
from nextcord import Interaction, SlashOption, PermissionOverwrite, Permissions, Colour, Embed, Attachment


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


async def read_class_json(file: Attachment) -> SectionJson:
    """
    reads a json file Attachment containing classes
    """

    content_type, encoding = file.content_type.split("; ")

    if content_type != "application/json":
        raise Exception(f"File must be a JSON file but was {content_type}")

    if encoding != "charset=utf-8":
        raise Exception(f"File must be encoded in UTF-8 but was {encoding}")

    file_contents = await file.read()

    data = json.loads(file_contents)

    if data["$schema"] != JSON_SCHEMA:
        raise Exception(f"Incorrect JSON schema\nExpected: {JSON_SCHEMA}\nFound: {data['$schema']}")

    return data


course_name_regex = re.compile('(COSC|MATH|STAT)[- ]([0-9]{3})', re.I)
term_name_regex = re.compile('([A-Z][a-z]+)[- ](20[0-9]{2})')


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
        logging.error(f"Issue with {category_name}.  Error: {sys.exc_info()[0]}")


async def create_channel(channel_name: str, category: nextcord.CategoryChannel, interaction: Interaction, description: str):
    """
    creates channel in category with description and name, returns channel object.
    """

    return await interaction.guild.create_text_channel(channel_name, category=category, topic=description)


async def create_role(interaction: Interaction, role_name: str, permissions: Permissions = Permissions.none(), color=Colour.default(), mentionable=False):
    """
    creates a role with specified permissions, with specifed name.
    """

    return await interaction.guild.create_role(name=role_name, permissions=permissions, colour=color, mentionable=mentionable)


async def create_role_for_category(interaction: Interaction, category: nextcord.CategoryChannel, term: str):
    role_name = f"{category.name.replace('-', ' ')} {term}"
    role = await create_role(interaction, role_name, color=nextcord.Colour.blue(), mentionable=True)
    # gives basic permissions to a role for its assigned channel
    await category.set_permissions(
        role,
        read_messages=True,
        send_messages=True,
        add_reactions=True,
        read_message_history=True
    )
    return role


def reaction_emoji() -> Generator[str, None, None]:
    """
    generates emojis for reactions
    """

    for letter in ascii_lowercase:
        yield f":regional_indicator_{letter}:"


class ChannelManager(Cog, name="channelmanager"):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="importclasses")
    @has_permissions(administrator=True)
    async def import_classes(self, interaction: Interaction, file: Attachment = SlashOption(description="A JSON file containing the classes.", required=True)):
        """
        Import a JSON file and create channels and roles for each class.
        """

        try:
            json = await read_class_json(file)
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
                else:
                    prof_lastname = "TBA"

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
            if course_name_regex.search(channel.name):
                coroutines.append(channel.delete())
                channels_count += 1

        for role in interaction.guild.roles:
            if course_name_regex.search(role.name):
                coroutines.append(role.delete())
                roles_count += 1

        await asyncio.gather(*coroutines)

        await interaction.followup.send(f"Deleted {channels_count} channels and categories and {roles_count} roles.")

    @nextcord.slash_command(name="classrolereactions")
    async def carl_class_roles(self, interaction: Interaction):
        """
        Generates the Carl bot commands to create reaction roles for all classes.
        """

        await interaction.response.defer()

        lower_level_roles: list[nextcord.Role] = []
        upper_level_roles: list[nextcord.Role] = []

        for role in interaction.guild.roles:
            match = course_name_regex.search(role.name)
            if match is not None and match.group(2)[0] in ['1', '2', '3']:
                lower_level_roles.append(role)
            elif match is not None and match.group(2)[0] in ['4', '5', '6']:
                upper_level_roles.append(role)

        term = term_name_regex.search(lower_level_roles[0].name).group(0)

        for role_group_name, roles in (("100-300", lower_level_roles), ("400-600", upper_level_roles)):
            roles.sort(key=lambda role: role.name)

            title = f"Use the following commands to create reaction roles for {role_group_name} classes."

            message = "```\n/reactionrole setup\n```\n"

            message += "Which channel would you like the message to be in?\n"
            message += "```\n#class-reaction-roles\n```\n"

            message += "What would you like the message to say?\n"
            message += "```\n"
            message += f"{term} Class Channels {role_group_name} | React to gain access to your class channels\n\n"
            for role, emoji in zip(roles, reaction_emoji()):
                message += f"{emoji}  {course_name_regex.search(role.name).group(0)}\n"
            message += "\n```\n"

            message += "Would you like the message to have a color?\n"
            message += "```\nnone\n```\n"

            message += "What roles would you like to add?\n"
            message += "```\n"
            for role, emoji in zip(roles, reaction_emoji()):
                message += f"{emoji} {role.mention}\n"
            message += "\n```\n"

            message += "```\ndone\n```\n"

            embed = Embed(title=title, description=message)

            await interaction.followup.send(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(ChannelManager(bot))
