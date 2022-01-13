import os
import sys
import random
import discord
import yaml
from discord.ext import commands

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick', pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, context, member: discord.Member, *args):
        """
        Kick a user out of the server.
        """
        if member.guild_permissions.administrator:
            embed = discord.Embed(
                title="Error!",
                description="User has Admin permissions.",
                color=config["error"]
            )
            await context.send(embed=embed)
        else:
            try:
                reason = " ".join(args)
                await member.kick(reason=reason)
                embed = discord.Embed(
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
                embed = discord.Embed(
                    title="Error!",
                    description="An error occurred while trying to kick the user.",
                    color=config["success"]
                )
                await context.message.channel.send(embed=embed)

    @commands.command(name="nick")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, context, member: discord.Member, *, name: str):
        """
        Change the nickname of a user on a server.
        """
        try:
            if name.lower() == "!reset":
                name = None
            await member.edit(nick=name)
            embed = discord.Embed(
                title="Changed Nickname!",
                description=f"**{member}'s** new nickname is **{name}**!",
                color=config["success"]
            )
            await context.send(embed=embed)
        except Exception as e:
            print(e)
            embed = discord.Embed(
                title="Error!",
                description="An error occurred while trying to change the nickname of the user.",
                color=config["success"]
            )
            await context.message.channel.send(embed=embed)
    
    @commands.command(name="clean")
    async def clean(self, context, num="1"):
        """
        Solves many problems. (Limited by Discord to max out at 333)
        """
        try:
            message = await context.channel.fetch_message(context.message.reference.message_id)
            reactions = ['🙅', '🙆', '🙇', '🙋', '🙌', '🙍', '🙎', '🙏', '✂', '✈', '✉', '✊', '✋', '✌', '✏', '❄', '❤', '🚀', '🚃', '🚄', '🚅', '🚇', '🚉', '🚌', '🚏', '🚑', '🚒', '🚓', '🚕', '🚗', '🚙', '🚚', '🚢', '🚤', '🚥', '🚧', '🚨', '🚩', '🚪', '🚫', '🚬', '🚲', '🚶', '🚽', '🛀', '⌚', '⌛', '⏰', '⏳', '☁', '☎', '☔', '☕', '♨', '♻', '♿', '⚓', '⚡', '⚽', '⚾', '⛄', '⛅', '⛪', '⛲', '⛳', '⛵', '⛺', '⭐', '⛽', '🃏', '🌀', '🌁', '🌂', '🌃', '🌄', '🌅', '🌆', '🌇', '🌈', '🌉', '🌊', '🌋', '🌏', '🌙', '🌛', '🌟', '🌠', '🌰', '🌱', '🌴', '🌵', '🌷', '🌸', '🌹', '🌺', '🌻', '🌼', '🌽', '🌾', '🌿', '🍀', '🍁', '🍂', '🍃', '🍄', '🍅', '🍆', '🍇', '🍈', '🍉', '🍊', '🍌', '🍍', '🍎', '🍏', '🍑', '🍒', '🍓', '🍔', '🍕', '🍖', '🍗', '🍘', '🍙', '🍚', '🍛', '🍝', '🍞', '🍟', '🍠', '🍡', '🍢', '🍣', '🍤', '🍥', '🍦', '🍧', '🍨', '🍩', '🍪', '🍫', '🍬', '🍭', '🍮', '🍯', '🍰', '🍱', '🍲', '🍳', '🍴', '🍵', '🍶', '🍷', '🍸', '🍹', '🍺', '🍻', '🎀', '🎁', '🎂', '🎃', '🎄', '🎅', '🎆', '🎇', '🎈', '🎉', '🎊', '🎋', '🎌', '🎍', '🎎', '🎏', '🎐', '🎑', '🎒', '🎓', '🎠', '🎡', '🎢', '🎣', '🎤', '🎥', '🎦', '🎧', '🎨', '🎩', '🎪', '🎫', '🎬', '🎭', '🎮', '🎯', '🎰', '🎱', '🎲', '🎳', '🎴', '🎵', '🎶', '🎷', '🎸', '🎹', '🎺',  '🎽', '🎾', '🎿', '🏀', '🏁', '🏂', '🏃', '🏄', '🏆', '🏈', '🏊', '🏠', '🏡', '🏢', '🏣', '🏥', '🏦', '🏧', '🏨', '🏩', '🏪', '🏫', '🏬', '🏭', '🏮', '🏯', '🏰', '🐌', '🐍', '🐎', '🐑', '🐒', '🐔', '🐗', '🐘', '🐙', '🐚', '🐛', '🐜', '🐝', '🐞', '🐟', '🐠', '🐡', '🐢', '🐣', '🐤', '🐥', '🐦', '🐧', '🐨', '🐩', '🐫', '🐬', '🐭', '🐮', '🐯', '🐰', '🐱', '🐲', '🐳', '🐴', '🐵', '🐶', '🐷', '🐸', '🐹', '🐺', '🐻', '🐼', '🐽', '🐾', '👀', '👂', '👃', '👄', '👅', '👆', '👇', '👈', '👉', '👊', '👋', '👌', '👍', '👎', '👏', '👐', '👑', '👒', '👓', '👔', '👕', '👖', '👗', '👘', '👙', '👚', '👛', '👜', '👝', '👞', '👟', '👠', '👡', '👢', '👣',  '👦', '👧', '👨', '👩', '👪', '👫', '👮', '👯', '👰', '👱', '👴', '👶', '👷', '👸', '👹', '👺', '👻', '👼', '👽', '👾', '👿', '💀', '💁', '💂', '💃', '💄', '💅', '💆', '💇', '💈', '💉', '💊', '💋', '💌', '💍', '💎', '💏', '💐', '💑', '💒', '💓', '💔', '💕', '💖', '💗', '💘', '💙', '💚', '💛', '💜', '💝', '💞', '💟', '💠', '💡', '💢', '💣', '💤', '💥', '💦', '💧', '💨', '💩', '💪', '💫', '💬', '💮', '💯', '💰', '💲', '💳', '💵', '💸', '💺', '💻', '💼', '💽', '💾',  '📀', '📃', '📅', '📆', '📈', '📉', '📌', '📍', '📎', '📓', '📔', '📕', '📖', '📞', '📟', '📠', '📡', '📣', '📦', '📧', '📫', '📰', '📱', '📷', '📹', '📺', '📻', '📼', '🔊', '🔋', '🔌', '🔎', '🔐', '🔑', '🔒', '🔓', '🔔', '🔜', '🔥', '🔦', '🔧', '🔨', '🔩', '🔪', '🔫', '🔮', '🗻', '🗼', '🗽', '🗾', '🗿', '😴', '🚁', '🚂', '🚆', '🚈', '🚊', '🚍', '🚎', '🚐', '🚔', '🚖', '🚘', '🚛', '🚜', '🚝', '🚞', '🚟', '🚠', '🚡', '🚣', '🚦', '🚮', '🚵', '🚿', '🛁', '🌍', '🌎', '🌜', '🌝', '🌞', '🌲', '🌳', '🍋', '🍐', '🍼', '🏇', '🏉', '🏤', '🐀', '🐁', '🐂', '🐃', '🐄', '🐅', '🐆', '🐇', '🐈', '🐉', '🐊', '🐋', '🐏', '🐐', '🐓', '🐕', '🐖', '🐪', '👭', '📬', '📭', '📯', '🔬', '🔭']
            for i in range(20):
                await message.add_reaction(random.choice(reactions))

        except:
            num = int(num)
            if num > 333:
                num = 333
            if (context.guild.id == 856919397754470420):
                res = ["<a:bdk:920426208498421840>"] * num
            else:
                res = [":yum:"] * num
            await context.reply("\n".join(res))      

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, context, member: discord.Member, *args):
        """
        Bans a user from the server.
        """
        try:
            if member.guild_permissions.administrator:
                embed = discord.Embed(
                    title="Error!",
                    description="User has Admin permissions.",
                    color=config["success"]
                )
                await context.send(embed=embed)
            else:
                reason = " ".join(args)
                await member.ban(reason=reason)
                embed = discord.Embed(
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
            embed = discord.Embed(
                title="Error!",
                description="An error occurred while trying to ban the user.",
                color=config["success"]
            )
            await context.send(embed=embed)

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, context, member: discord.Member, *args):
        """
        Warns a user in their private messages.
        """
        reason = " ".join(args)
        embed = discord.Embed(
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
