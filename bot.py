"""
This is the main file that runs the bot.
"""


import os
import platform
import nextcord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from nextcord.ext import commands
from nextcord.ext.commands import Bot

from noncommands import auto_code_block, quotes
from constants import ERROR_COLOR, config


intents = nextcord.Intents.default().all()

bot = Bot(intents=intents, command_prefix="!")

scheduler = AsyncIOScheduler()
toSchedule = quotes.Quotes(bot)
autoCodeBlock = auto_code_block.AutoCodeBlock(bot)


@bot.event
async def on_ready():
    """
    The code in this even is executed when the bot is ready
    """

    print(f"Logged in as {bot.user.name}")
    print(f"nextcord.py API version: {nextcord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    await bot.change_presence(activity=nextcord.Game("/help"))

# Removes the default help command of nextcord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


@bot.event
async def on_message(message):
    """
    The code in this event is executed every time someone sends a message, with or without the prefix
    """

    # Ignores if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    # Ignores if a command is being executed by a blacklisted user

    if message.author.id in config["blacklist"]:
        return

    await autoCodeBlock.check_message(message)

    await bot.process_commands(message)


@bot.event
async def on_command_completion(ctx):
    """
    The code in this event is executed every time a command has been *successfully* executed
    """
    full_command_name = ctx.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    print(
        f"Executed {executed_command} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")


@bot.event
async def on_command_error(context, error):
    """
    The code in this event is executed every time a valid commands catches an error
    """

    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = nextcord.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=ERROR_COLOR
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = nextcord.Embed(
            title="Error!",
            description="You are missing the permission `" + ", ".join(
                error.missing_perms) + "` to execute this command!",
            color=ERROR_COLOR
        )
        await context.send(embed=embed)
    raise error

scheduler.add_job(toSchedule.daily_quote,
                  CronTrigger(hour="8", minute="0", second="0", day_of_week="0-4", timezone="EST"))
scheduler.start()
bot.run(config["token"])
