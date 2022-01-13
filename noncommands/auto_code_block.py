import re
import asyncio

class AutoCodeBlock:
    def __init__(self, bot):
        self.bot = bot

    async def check_message(self, context):
        message_text = context.message.content
        if re.search('({[^]*})', message_text) and ("```" not in message_text or "```\n" in message_text):
            probable_code = message_text.replace("```", "")
            reply = "It seems like that message might contain some unformatted code, I did my best to format it for you. If this is unwanted, react to this message."
            reply += "\n```java\n"
            reply += probable_code
            reply += "\n```\n"
            reply += "(If you are curious how to do this, check out https://www.codegrepper.com/code-examples/whatever/discord+syntax+highlighting)"
            reply += f'Original Message sent by: {context.message.author.username}'

            msg = await context.reply(reply)

            try:
                await self.bot.wait_for("reaction_add", timeout=120)
                msg.delete()
            except asyncio.exceptions.TimeoutError:
                pass




