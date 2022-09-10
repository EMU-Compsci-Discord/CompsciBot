import os
import sys

import yaml
from nextcord.ext import commands
import mysql.connector
import json
from noncommands import quotes


with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Here we name the cog and create a new class for the cog.
class Quotes(commands.Cog, name="quotes"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.command(name="populatequotes")
    async def populatequotes(self, context):
        """
        [No arguments] This puts the quotes from quotes.json into the database
        """
        await context.send("Adding quotes to database...")
        mydb = mysql.connector.connect(
            host=config["dbhost"],
            user=config["dbuser"],
            password=config["dbpassword"],
            database=config["databasename"],
            autocommit=True,
            use_unicode=True
        )

        mycursor = mydb.cursor(buffered=True)
        mycursor.execute('SET NAMES utf8mb4')
        mycursor.execute("SET CHARACTER SET utf8mb4")
        mycursor.execute("SET character_set_connection=utf8mb4")

        f = open("resources/quotes.json", encoding="utf-8")
        json_data = json.load(f)
        quotes = list(json_data['teacherQuotes'])

        for quote in quotes:
            sql = "INSERT INTO quotes (quote) VALUES (%s)"
            val = (quote,)
            mycursor.execute(sql, val)
        
        mydb.commit()
        mycursor.close()
        mydb.close()
        await context.send("Quotes added to database")
    
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
