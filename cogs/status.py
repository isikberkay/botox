import discord
from discord.ext import tasks, commands
import random

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()  # Start the task when the cog is loaded

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_ready(self):
        print("Cog - Status is loaded.")

    def cog_unload(self):
        self.change_status.cancel()  # Properly cancel the task when the cog is unloaded

    statuses = [
        discord.Game("Detroit: Become Human"),
        discord.Streaming(name="Just coding", url="http://twitch.tv/summit1g"),
        discord.Activity(type=discord.ActivityType.listening, name="Lofi Beats"),
        discord.Activity(type=discord.ActivityType.watching, name="Person of Interest"),
        discord.Activity(type=discord.ActivityType.listening, name="ASMR"),
    ]

    @tasks.loop(minutes=10)
    async def change_status(self):
        await self.bot.change_presence(activity=random.choice(self.statuses))

    @change_status.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()  # Wait until the bot logs in

def setup(bot):
    bot.add_cog(StatusCog(bot))
