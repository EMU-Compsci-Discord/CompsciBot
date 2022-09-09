import os
import sys
import random
import nextcord
import yaml
from nextcord.ext import commands


with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick', pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, context, member: nextcord.Member, *args):
        """
        Kick a user out of the server.
        """
        if member.guild_permissions.administrator:
            embed = nextcord.Embed(
                title="Error!",
                description="User has Admin permissions.",
                color=config["error"]
            )
            await context.send(embed=embed)
        else:
            try:
                reason = " ".join(args)
                await member.kick(reason=reason)
                embed = nextcord.Embed(
                    title="User Kicked!",
                    description=f"**{member}** was kicked by **{context.message.author}**!",
                    color=config["success"]
                )
                embed.add_field(
                    name="Reason:",
                    value=reason
                )
                await context.send(embed=embed)
                try:
                    await member.send(
                        f"You were kicked by **{context.message.author}**!\nReason: {reason}"
                    )
                except:
                    pass
            except:
                embed = nextcord.Embed(
                    title="Error!",
                    description="An error occurred while trying to kick the user.",
                    color=config["success"]
                )
                await context.message.channel.send(embed=embed)

    @commands.command(name="nick")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, context, member: nextcord.Member, *, name: str):
        """
        Change the nickname of a user on a server.
        """
        try:
            if name.lower() == "!reset":
                name = None
            await member.edit(nick=name)
            embed = nextcord.Embed(
                title="Changed Nickname!",
                description=f"**{member}'s** new nickname is **{name}**!",
                color=config["success"]
            )
            await context.send(embed=embed)
        except Exception as e:
            print(e)
            embed = nextcord.Embed(
                title="Error!",
                description="An error occurred while trying to change the nickname of the user.",
                color=config["success"]
            )
            await context.message.channel.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, context, member: nextcord.Member, *args):
        """
        Bans a user from the server.
        """
        try:
            if member.guild_permissions.administrator:
                embed = nextcord.Embed(
                    title="Error!",
                    description="User has Admin permissions.",
                    color=config["success"]
                )
                await context.send(embed=embed)
            else:
                reason = " ".join(args)
                await member.ban(reason=reason)
                embed = nextcord.Embed(
                    title="User Banned!",
                    description=f"**{member}** was banned by **{context.message.author}**!",
                    color=config["success"]
                )
                embed.add_field(
                    name="Reason:",
                    value=reason
                )
                await context.send(embed=embed)
                await member.send(f"You were banned by **{context.message.author}**!\nReason: {reason}")
        except:
            embed = nextcord.Embed(
                title="Error!",
                description="An error occurred while trying to ban the user.",
                color=config["success"]
            )
            await context.send(embed=embed)

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, context, member: nextcord.Member, *args):
        """
        Warns a user in their private messages.
        """
        reason = " ".join(args)
        embed = nextcord.Embed(
            title="User Warned!",
            description=f"**{member}** was warned by **{context.message.author}**!",
            color=config["success"]
        )
        embed.add_field(
            name="Reason:",
            value=reason
        )
        await context.send(embed=embed)
        try:
            await member.send(f"You were warned by **{context.message.author}**!\nReason: {reason}")
        except:
            pass


def setup(bot):
    bot.add_cog(moderation(bot))
