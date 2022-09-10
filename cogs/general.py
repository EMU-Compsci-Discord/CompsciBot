import os
import platform
import sys
import json
import yaml
import random
from nextcord.ext import commands
from noncommands import summarizer, quotes
import nextcord
from typing import Optional
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel

with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class general(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="info", description="Get some useful (or not) information about the bot.")
    async def info(self, interaction: Interaction):
        """
        [No Arguments] Get some useful (or not) information about the bot.
        """
        embed = nextcord.Embed(
            description="The server's most helpful member.",
            color=config["success"]
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="Nanosplitter#4549",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}"
        )
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="serverinfo", description="Get some useful (or not) information about the server.")
    async def serverinfo(self, interaction: Interaction):
        """
        [No Arguments] Get some useful (or not) information about the server.
        """
        server = interaction.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = nextcord.Embed(
            title="**Server Name:**",
            description=f"{server}",
            color=config["success"]
        )

        if server.icon != None:
            embed.set_thumbnail(
                url=server.icon.url
            )
        embed.add_field(
            name="Server ID",
            value=server.id
        )
        embed.add_field(
            name="Member Count",
            value=server.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{channels}"
        )
        embed.add_field(
            name=f"Roles ({role_length})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {time}"
        )
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="ping", description="Check if the bot is alive.")
    async def ping(self, interaction: Interaction):
        """
        [No Arguments] Check if the bot is alive.
        """
        embed = nextcord.Embed(
            color=config["success"]
        )
        embed.add_field(
            name="Pong!",
            value=":ping_pong:",
            inline=True
        )
        embed.set_footer(
            text=f"Pong request by {interaction.user}"
        )
        await interaction.response.send_message(embed=embed)  

    @nextcord.slash_command(name="invite", description="Get the invite link of the bot to be able to invite it to another server.")
    async def invite(self, interaction: Interaction):
        """
        [No Arguments] Get the invite link of the Dad to be able to invite him to another server.
        """
        await interaction.response.send_message(f"Invite me by clicking here: https://discordapp.com/oauth2/authorize?&client_id={config['application_id']}&scope=bot&permissions=8")

    
    @nextcord.slash_command(name="tldrchannel", description="Get a TLDR of X number of past messages on the channel.")
    async def tldrchannel(self, interaction: Interaction, number: int = SlashOption(description="The number of past messages to summarize", required=True, min_value=5, max_value=200)):
        """
        [NumberOfMessages] Get a TLDR of X number of past messages on the channel.
        """

        messages = await interaction.channel.history(limit=number).flatten()
        text = ". ".join([m.content for m in messages])
        text = text.replace(".. ", ". ")
        embed = summarizer.getSummaryText(config, text)

        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="tldr", description="Get a TLDR of a web page.")
    async def tldr(self, interaction: Interaction, url: str = SlashOption(description="The URL of the web page to summarize", required=True)):
        """
        [URL] Get a TLDR a web page.
        """
        try:
            await interaction.response.send_message(embed=summarizer.getSummaryUrl(config, url))
        except:
            await interaction.response.send_message("There's something odd about that link. Either they won't let me read it or you sent it wrongly.")

    @nextcord.slash_command(name="poll", description="Create a poll where members can vote.")
    async def poll(self, interaction: Interaction, question: str = SlashOption(description="Question to ask members.", required=True)):
        """
        [Question] Create a poll where members can vote.
        """
        embed = nextcord.Embed(
            title="A new poll has been created!",
            description=f"{question}",
            color=config["success"]
        )

        embed.set_footer(
            text=f"Poll created by: {interaction.user} • React to vote!"
        )
        
        embed_message = await interaction.response.send_message(embed=embed)
        embed_message = await embed_message.fetch()
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

def setup(bot):
    bot.add_cog(general(bot))
