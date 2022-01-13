import os
import platform
import random
import sys
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
# import schedule
from noncommands import haikudetector
from noncommands import imchecker
from noncommands import reminderLoop
from noncommands import antimayhem
from noncommands import scooby

import discord
import yaml
from discord.ext import commands, tasks
from discord.ext.commands import Bot

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

intents = discord.Intents.default()

bot = Bot(command_prefix=config["bot_prefix"], intents=intents)

imChecker = imchecker.ImChecker()
reminderChecker = reminderLoop.ReminderLoop()
antiMayhem = antimayhem.AntiMayhem()
haikuDetector = haikudetector.HaikuDetector()
scooby = scooby.Scooby(bot)

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()


# Setup the game status task of the bot
@tasks.loop(minutes=1.0)
async def status_task():
    statuses = ["with your mom"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
    # Ignores if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    # Ignores if a command is being executed by a blacklisted user

    if message.author.id in config["blacklist"]:
        return
    
    await imChecker.checkIm(message)

    await antiMayhem.gotem(message)

    await haikuDetector.checkForHaiku(message)

    await bot.process_commands(message)




# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    print(
        f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(context, error):
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=config["error"]
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="You are missing the permission `" + ", ".join(
                error.missing_perms) + "` to execute this command!",
            color=config["error"]
        )
        await context.send(embed=embed)
    raise error

@tasks.loop(seconds=5)
async def checkReminders():
    await reminderChecker.checkReminders(bot)
    await reminderChecker.deleteOldReminders(bot)

checkReminders.start()
scheduler = AsyncIOScheduler()
scheduler.add_job(scooby.whatsTheMove, CronTrigger(hour = "19", minute = "0", second = "0", timezone="EST"))
scheduler.add_job(scooby.praiseFireGator, CronTrigger(day_of_week="thu", hour = "0", minute = "0", second = "0", timezone="EST"))
scheduler.start()
bot.run(config["token"])
