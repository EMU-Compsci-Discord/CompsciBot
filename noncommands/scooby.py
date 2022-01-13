class Scooby:
    def __init__(self, bot):
        self.bot = bot
    async def whatsTheMove(self):
        c = self.bot.get_channel(856919399789625376)
        await c.send("***What's The Move?***")
    
    async def praiseFireGator(self):
        c = self.bot.get_channel(856919399789625376)
        await c.send("***PRAISE***")