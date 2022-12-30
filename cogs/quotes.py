"""
This cog adds commands for getting and creating quotes.
"""


from noncommands import quotes
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption


class Quotes(commands.Cog, name="quotes"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @nextcord.slash_command(name="quote", description="Searches CS quotes by keyword, or search one at random.")
    async def quote(self, interaction: Interaction, keyword: str = SlashOption(description="The quote to submit", default="", required=False)):
        """
        [(Optional) Search text] Searches CS quotes by keyword, or search one at random.
        """
        quote_class = quotes.Quotes(self.bot)
        random_quote = await quote_class.quote(keyword)
        await interaction.response.send_message(random_quote)

    @nextcord.slash_command(name="newquote", description="Creates a new quote to be put into the list of CS quotes.")
    async def newquote(self, interaction: Interaction, quote: str = SlashOption(description="The quote to submit", required=True)):
        """
        [(Required) Quote] Creates a new quote to be put into the list of CS quotes.
        """
        quote_class = quotes.Quotes(self.bot)
        newquote = await quote_class.newquote(quote)

        await interaction.response.send_message("Quote submitted! Quote: " + newquote)


def setup(bot):
    bot.add_cog(Quotes(bot))
