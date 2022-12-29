import asyncio
import os
import random
import sys
import aiohttp
import aiofiles
import hashlib
import yaml
import requests
import uuid
import inspirobot
import uwuify
import json

import nextcord
from typing import Optional
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel


with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="dadjoke", description="Get one of the classics")
    async def dadjoke(self, interaction: Interaction, searchterm: str = SlashOption(description="A term to try and find a dadjoke about", default="", required=False)):
        """
        [(Optional)SearchTerm] Get one of the classics.
        """
        url = "https://icanhazdadjoke.com/search?term=" + searchterm
        headers = {'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        json = r.json()
        try:
            await interaction.response.send_message(random.choice(json["results"])["joke"])
        except:
            await interaction.response.send_message("I don't think I've heard a good one about that yet. Try something else.")

    @nextcord.slash_command(name="xkcd", description="Get an xkcd comic.")
    async def xkcd(self, interaction: Interaction, comicnumber: int = SlashOption(description="A specific xkcd comic, like '1' to get the first comic", default="", required=False)):
        """
        [(Optional)xkcdNumber] Retrieve a random or specific xkcd comic
        """
        r = requests.get("http://xkcd.com/info.0.json")
        comicnumber = comicnumber if comicnumber != "" else str(random.choice(range(1, r.json()['num'])))

        r = requests.get("http://xkcd.com/" + str(comicnumber) + "/info.0.json")

        try:
            await interaction.response.send_message(r.json()['img'])
        except:
            await interaction.response.send_message("I can't find that xkcd comic, try another.")

    @nextcord.slash_command(name="iswanted", description="See if someone is on the FBI's most wanted list.")
    async def iswanted(self, interaction: Interaction, name: str = SlashOption(description="The name of the person you want to check", required=True)):
        """
        [SearchTerm] See if someone is on the FBI's most wanted list.
        """
        r = requests.get("https://api.fbi.gov/wanted/v1/list", params={"title": name})

        try:
            url = random.choice(r.json()['items'])["files"][0]['url']
            await interaction.response.send_message(name + " might be wanted by the FBI:\n" + url)
        except:
            await interaction.response.send_message("No one with that name is currently wanted by the FBI")

    @nextcord.slash_command(name="eightball", description="Ask any yes/no question and get an answer.")
    async def eight_ball(self, interaction: Interaction, question: str = SlashOption(description="The question you want to ask", required=True)):
        """
        [Question] Ask any question to the bot.
        """
        answers = ['It is certain.', 'It is decidedly so.', 'You may rely on it.', 'Without a doubt.',
                   'Yes - definitely.', 'As I see, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                   'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.',
                   'Cannot predict now.', 'Concentrate and ask again later.', 'Don\'t count on it.', 'My reply is no.',
                   'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        embed = nextcord.Embed(
            title=f"**My Answer to '{question}':**",
            description=f"{answers[random.randint(0, len(answers) - 1)]}",
            color=config["success"]
        )
        embed.set_footer(
            text=f"Question asked by: {interaction.user}"
        )

        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="randomfact", description="The world has so much to offer, let's learn about it!")
    async def randomfact(self, interaction: Interaction):
        """
        [No Arguments] Get a random fact.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://nextcordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as request:
                if request.status == 200:
                    data = await request.json()
                    embed = nextcord.Embed(description=data["text"], color=config["main_color"])
                    await interaction.response.send_message(embed=embed)
                else:
                    embed = nextcord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=config["error"]
                    )
                    await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="inspire", description="Get an inspirational poster courtesy of https://inspirobot.me/")
    async def inspire(self, interaction: Interaction):
        """
        [No Arguments] Get an inspirational poster courtesy of https://inspirobot.me/
        """
        quote = inspirobot.generate()
        await interaction.response.send_message(quote.url)

    @nextcord.slash_command(name="wisdom", description="Get some wisdom courtesy of https://inspirobot.me/")
    async def wisdom(self, interaction: Interaction):
        """
        [No Arguments] Get some wisdom courtesy of https://inspirobot.me/
        """
        flow = inspirobot.flow()  # Generate a flow object
        res = ""
        for quote in flow:
            res += quote.text + "\n"

        await interaction.response.send_message(res)

    @nextcord.slash_command(name="advice", description="Get some advice.")
    async def advice(self, interaction: Interaction):
        """
        [No Arguments] Get some advice.
        """
        r = requests.get("https://api.adviceslip.com/advice")
        await interaction.response.send_message(r.json()['slip']['advice'])


def setup(bot):
    bot.add_cog(Fun(bot))
