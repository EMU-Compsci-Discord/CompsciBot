import asyncio
import os
import random
import sys

import aiohttp
import aiofiles
import hashlib
import discord
import yaml
from discord.ext import commands
from discord.ext.commands import BucketType
import requests
import uuid
import inspirobot
import uwuify
import language_tool_python
import contractions

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.languageTool = language_tool_python.LanguageTool('en-US')
        self.bot = bot

def setup(bot):
    bot.add_cog(Fun(bot))
