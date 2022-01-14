import re
import asyncio

class AutoCodeBlock:
    def __init__(self, bot):
        self.bot = bot

    async def check_message(self, message):
        message_text = message.content
        if re.search('\{*.\}', message_text) and ("```" not in message_text or "```\n" in message_text):
            probable_code = message_text.replace("```", "")
            reply = "It seems like that message might contain some unformatted code, I did my best to format it for you. If this is unwanted, react to this message within 2 minutes."
            reply += "\n```java\n"
            reply += probable_code
            reply += "\n```\n"
            reply += "(If you are curious how to do this, check out https://www.codegrepper.com/code-examples/whatever/discord+syntax+highlighting)"
            reply += f'\nOriginal Message sent by: {message.author.mention}'

            msg = await message.reply(reply)
            await msg.add_reaction("🚫")

            def check(reaction, user):
                return user == message.author and str(reaction) in "🚫"

            try:
                await self.bot.wait_for("reaction_add", timeout=120, check=check)
                await msg.delete()
            except asyncio.exceptions.TimeoutError:
                await msg.clear_reactions()
                pass




