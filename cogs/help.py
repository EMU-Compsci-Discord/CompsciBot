"""
This cog adds a help command.
"""


import nextcord
from nextcord.ext import commands
from nextcord import Interaction


class Help(commands.Cog, name="help"):
    """
    This cog adds a help command.
    """

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="How do I find out what all the commands are?")
    async def help(self, interaction: Interaction):
        """
        How do I find out what all the commands are?
        """

        await interaction.response.send_message("This bot uses slash commands! Type a `/` into the chat, click my icon, and you should see all the commands I can take!")


def setup(bot):
    bot.add_cog(Help(bot))
