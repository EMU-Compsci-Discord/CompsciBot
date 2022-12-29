import yaml
import nextcord
from nextcord.ext import commands
from nextcord import Interaction


with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


class Help(commands.Cog, name="help"):
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
