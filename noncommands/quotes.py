import json
import random
import yaml
import os
import re

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


class Quotes:
    def __init__(self, bot):
        self.bot = bot

    async def dailyQuote(self):
        c = self.bot.get_channel(707293854507991172)
        dailyquote = await Quotes.quote(self.bot, "")
        await c.send("Daily Quote:\n"+dailyquote)

    async def quote(self, keywords):

        f = open("resources/quotes.json", encoding="utf-8")
        json_data = json.load(f)
        quotes = list(json_data['teacherQuotes'])
        matches = []

        if keywords:
            random_quote = "Sorry! You made a bad search"
            for line in quotes:
                if re.search(keywords, line, re.IGNORECASE):
                    matches.append(line)
            if matches:
                random_quote = random.choice(matches)
        else:
            random_quote = random.choice(quotes)
        return random_quote

    async def newquote(self, context):
        prefix = config["bot_prefix"]
        startLen = len(prefix) + len("newquote")
        quote = context.message.content[startLen:]

        with open("resources/quotes.json", "r", encoding="utf-8") as qfile:
            qjson = json.load(qfile)
            qjson["teacherQuotes"].append(quote)
            qfile = open("resources/quotes.json", "w")
            json.dump(qjson, qfile)

        return quote
