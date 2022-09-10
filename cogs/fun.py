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
    async def dadjoke(self, interaction: Interaction, searchterm: Optional[str] = SlashOption(description="A term to try and find a dadjoke about", default="", required=False)):
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
    async def xkcd(self, interaction: Interaction, comicnumber: Optional[int] = SlashOption(description="A specific xkcd comic, like '1' to get the first comic", default="", required=False)):
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
    async def iswanted(self, interaction: Interaction, name: Optional[str] = SlashOption(description="The name of the person you want to check", required=True)):
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
    async def eight_ball(self, interaction: Interaction, question: Optional[str] = SlashOption(description="The question you want to ask", required=True)):
        """
        [Question] Ask any question to the bot.
        """
        answers = ['It is certain.', 'It is decidedly so.', 'You may rely on it.', 'Without a doubt.',
                   'Yes - definitely.', 'As I see, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                   'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.',
                   'Cannot predict now.', 'Concentrate and ask again later.', 'Don\'t count on it.', 'My reply is no.',
                   'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        embed = nextcord.Embed(
            title="**My Answer:**",
            description=f"{answers[random.randint(0, len(answers) - 1)]}",
            color=config["success"]
        )
        embed.set_footer(
            text=f"Question asked by: {interaction.user}"
        )

        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))