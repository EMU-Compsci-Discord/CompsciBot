import mysql.connector

from constants import config


class Quotes:
    def __init__(self, bot):
        self.bot = bot

    async def daily_quote(self):
        channel = self.bot.get_channel(707293854507991172)
        dailyquote = await Quotes.quote(self.bot, "")
        await channel.send("Daily Quote:\n" + dailyquote)

    async def quote(self, keywords):
        if config["db"] is None:
            return "Database not configured"

        mydb = mysql.connector.connect(
            host=config["db"]["host"],
            user=config["db"]["user"],
            password=config["db"]["password"],
            database=config["db"]["database"],
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
        if config["db"] is None:
            return "Database not configured"

        mydb = mysql.connector.connect(
            host=config["db"]["host"],
            user=config["db"]["user"],
            password=config["db"]["password"],
            database=config["db"]["database"],
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
