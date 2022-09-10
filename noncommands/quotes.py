import json
import random
import yaml
import os
import mysql.connector

with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class Quotes:
    def __init__(self, bot):
        self.bot=bot

    async def dailyQuote(self):
        channel = self.bot.get_channel(707293854507991172)
        dailyquote = await Quotes.quote(self.bot, "")
        await channel.send("Daily Quote:\n" + dailyquote)

    async def quote(self, keywords):
        mydb = mysql.connector.connect(
            host=config["dbhost"],
            user=config["dbuser"],
            password=config["dbpassword"],
            database=config["databasename"],
            autocommit=True,
            use_unicode=True
        )
        mycursor = mydb.cursor(buffered=True)
        sql = "SELECT quote FROM quotes WHERE quote LIKE %s ORDER BY RAND() LIMIT 1"
        val = ("%" + keywords + "%",)
        mycursor.execute(sql, val)
        quote = mycursor.fetchone()
        mycursor.close()
        mydb.close()

        if quote is None:
            return "No quotes found with that keyword"
        else:
            return quote[0]

    async def newquote(self, quote):
        mydb = mysql.connector.connect(
            host=config["dbhost"],
            user=config["dbuser"],
            password=config["dbpassword"],
            database=config["databasename"],
            autocommit=True,
            use_unicode=True
        )
        mycursor = mydb.cursor(buffered=True)
        sql = "INSERT INTO quotes (quote) VALUES (%s)"
        val = (quote,)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        mydb.close()
        
        return quote    