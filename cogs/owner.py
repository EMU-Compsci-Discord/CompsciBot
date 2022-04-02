import os
import sys

import nextcord
import yaml
from nextcord.ext import commands

if "CompsciBot" not in str(os.getcwd()):
    os.chdir("./CompsciBot")
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown")
    async def shutdown(self, context):
        """
        [No arguments] Make the bot shutdown
        """
        if context.message.author.id in config["owners"]:
            embed = nextcord.Embed(
                description="Shutting down. Bye! :wave:",
                color=config["success"]
            )
            await context.send(embed=embed)
            await self.bot.logout()
            await self.bot.close()
        else:
            embed = nextcord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await context.send(embed=embed)

    @commands.command(name="say", aliases=["echo"])
    async def say(self, context, *, args):
        """
        [(Required) Words] The bot will say anything you want.
        """
        if context.message.author.id in config["owners"]:
            await context.message.delete()
            await context.send(args)
            
        else:
            embed = nextcord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await context.send(embed=embed)

    @commands.command(name="embed")
    async def embed(self, context, *, args):
        """
         [(Required) Words] The bot will say anything you want, but within embeds.
        """
        if context.message.author.id in config["owners"]:
            embed = nextcord.Embed(
                description=args,
                color=config["success"]
            )
            await context.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await context.send(embed=embed)

    @commands.group(name="blacklist")
    async def blacklist(self, context):
        """
        [(Required) User] Lets you add or remove a user from not being able to use the bot.
        """
        if context.invoked_subcommand is None:
            embed = nextcord.Embed(
                title=f"There are currently {len(config['blacklist'])} blacklisted IDs",
                description=f"{config['blacklist']}",
                color=0x0000FF
            )
            await context.send(embed=embed)

    @blacklist.command(name="add")
    async def blacklist_add(self, context, member: nextcord.Member):
        """
        [(Required) User] Lets you add a user from not being able to use the bot.
        """
        if context.message.author.id in config["owners"]:
            userID = member.id
            try:
                config["blacklist"].append(userID)
                embed = nextcord.Embed(
                    title="User Blacklisted",
                    description=f"**{member.name}** has been successfully added to the blacklist",
                    color=config["success"]
                )
                embed.set_footer(
                    text=f"There are now {len(config['blacklist'])} users in the blacklist"
                )
                await context.send(embed=embed)
            except:
                embed = nextcord.Embed(
                    title="Error!",
                    description=f"An unknown error occurred when trying to add **{member.name}** to the blacklist.",
                    color=config["error"]
                )
                await context.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await context.send(embed=embed)

    @blacklist.command(name="remove")
    async def blacklist_remove(self, context, member: nextcord.Member):
        """
        [(Required) User] Lets you remove a user from not being able to use the bot.
        """
        if context.message.author.id in config["owners"]:
            userID = member.id
            try:
                config["blacklist"].remove(userID)
                embed = nextcord.Embed(
                    title="User Unblacklisted",
                    description=f"**{member.name}** has been successfully removed from the blacklist",
                    color=config["success"]
                )
                embed.set_footer(
                    text=f"There are now {len(config['blacklist'])} users in the blacklist"
                )
                await context.send(embed=embed)
            except:
                embed = nextcord.Embed(
                    title="Error!",
                    description=f"An unknown error occurred when trying to remove **{member.name}** from the blacklist.",
                    color=config["error"]
                )
                await context.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await context.send(embed=embed)


def setup(bot):
    bot.add_cog(owner(bot))
