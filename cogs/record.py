import discord
from discord.ext import commands

class Record(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_ready(self):
        print("Cog - Record is loaded.")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Record(bot)) # add the cog to the bot