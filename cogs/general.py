import os
import platform
import sys
import json
import discord
import yaml
import random
from discord.ext import commands
from noncommands import summarizer, quotes

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class general(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["botinfo"])
    async def info(self, context):
        """
        [No arguments] Get some useful (or not) information about the bot.
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
        [No arguments] Get some useful (or not) information about the server.
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
        [No arguments] Check if the bot is alive.
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
        newquote=await quoteClass.newquote(context)

        await context.send("Quote submitted! Quote: " + newquote)

    @commands.command(name="invite")
    async def invite(self, context):
        """
        [No arguments] Get the invite link of the bot to be able to invite it to another server.
        """
        await context.reply(f"Invite me by clicking here: https://discordapp.com/oauth2/authorize?&client_id={config['application_id']}&scope=bot&permissions=8")
    
    @commands.command(name="tldr")
    async def tldr(self, context, url):
        """
        [(Required) Link to site] Used skills I learned in the information retreival class to build this!
        """
        try:
            await context.send(embed=summarizer.getSummary(config, url))
        except:
             await context.send("There's something odd about that link. Either they won't let me read it or you sent it wrongly.")

    @commands.command(name="poll")
    async def poll(self, context, *args):
        """
        [(Required) Question] Create a poll where members can vote on a question.
        """
        poll_title = " ".join(args)
        embed = discord.Embed(
            title="A new poll has been created!",
            description=f"{poll_title}",
            color=config["success"]
        )
        embed.set_footer(
            text=f"Poll created by: {context.message.author} • React to vote!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

def setup(bot):
    bot.add_cog(general(bot))
