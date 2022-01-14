import os
import platform
import sys
import json
import discord
import yaml
import random
from discord.ext import commands

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

class general(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["botinfo"])
    async def info(self, context):
        """
        Get some useful (or not) information about the bot.
        """
        embed = discord.Embed(
            description="CompsciBot",
            color=config["success"]
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="Nanosplitter#4549",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"{config['bot_prefix']}",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {context.message.author}"
        )
        await context.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, context):
        """
        Get some useful (or not) information about the server.
        """
        server = context.message.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{server}",
            color=config["success"]
        )
        embed.set_thumbnail(
            url=server.icon_url
        )
        embed.add_field(
            name="Server ID",
            value=server.id
        )
        embed.add_field(
            name="Member Count",
            value=server.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{channels}"
        )
        embed.add_field(
            name=f"Roles ({role_length})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {time}"
        )
        await context.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, context):
        """
        Check if the bot is alive.
        """
        embed = discord.Embed(
            color=config["success"]
        )
        embed.add_field(
            name="Pong!",
            value=":ping_pong:",
            inline=True
        )
        embed.set_footer(
            text=f"Pong request by {context.message.author}"
        )
        await context.send(embed=embed)

    # Search CSquotes for a specific or give random quote
    @commands.command(name="quote")
    async def quote(self, context,*args):
        """
            Searches CS quotes by keyword, or search one at random.
        """
        #initialize and get data
        f = open("resources/quotes.json")
        json_data = json.load(f)
        quotes = list(json_data['CSQuotes'])

        #if keywords
        if args:
            keyTerm= " ".join(args)

            random_quote="Sorry! You made a bad search"
            for line in quotes:
                if keyTerm in line:
                    random_quote = line
                    break;
        #no keywords      
        else:
            random_quote = random.choice(quotes)
        await context.send(random_quote)
    
    # when called creates a new quote in CSQuotes field
    @commands.command(name="newquote")
    async def newquote(self, context, *args):
        """
            Creates a new quote to be put into the list of CS quotes.
        """
        quote = " ".join(args)
        qfile = open("resources/quotes.json","r")
        qjson = json.load(qfile)
        qfile.close()

        qjson["CSQuotes"].append(quote)
        qfile = open("resources/quotes.json","w")
        json.dump(qjson, qfile)

        await context.reply(f"New quote created: {quote}")

    @commands.command(name="invite")
    async def invite(self, context):
        """
        Get the invite link of the bot to be able to invite it to another server.
        """
        await context.reply(f"Invite me by clicking here: https://discordapp.com/oauth2/authorize?&client_id={config.application_id}&scope=bot&permissions=8")

def setup(bot):
    bot.add_cog(general(bot))
