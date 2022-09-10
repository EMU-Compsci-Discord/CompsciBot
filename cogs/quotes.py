import os
import sys
import yaml
from nextcord.ext import commands
from noncommands import quotes

with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Here we name the cog and create a new class for the cog.
class Quotes(commands.Cog, name="quotes"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.command(name="quote")
    async def quote(self, context, **kwargs):
        """
        [(Optional) Search text] Searches CS quotes by keyword, or search one at random.
        """
        quoteClass = quotes.Quotes(self.bot)
        prefix = config["bot_prefix"]
        startLen = len(prefix) + len("quote ")
        search = context.message.content[startLen:]
        random_quote = await quoteClass.quote(search)
        await context.send(random_quote)

    @commands.command(name="newquote")
    async def newquote(self, context):
        """
        [(Required) Quote] Creates a new quote to be put into the list of CS quotes.
        """
        quoteClass = quotes.Quotes(self.bot)
        newquote = await quoteClass.newquote(context)

        await context.send("Quote submitted! Quote: " + newquote)
            
# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Quotes(bot))
