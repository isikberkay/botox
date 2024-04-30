import discord
from discord.ext import commands

from discord import FFmpegPCMAudio
import os
import random

class Troll(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
        self.directory = './audio' # The directory containing the MP3 files

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_ready(self):
        print("Cog - Troll is loaded.")

    def get_random_mp3(self):
        """Returns the full path of a randomly chosen MP3 file from the directory."""
        if os.path.exists(self.directory) and os.path.isdir(self.directory):
            files = os.listdir(self.directory)
            mp3_files = [file for file in files if file.endswith('.mp3')]
            if mp3_files:
                chosen_file = random.choice(mp3_files)
                return os.path.join(self.directory, chosen_file)
        return None
    
    @commands.command(aliases=["gel"], pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
        await ctx.send(f"Joined {voice_channel}")

        file_path = self.get_random_mp3()
        if file_path:
            source = FFmpegPCMAudio(file_path)
            ctx.voice_client.play(source)
        else:
            await ctx.send("No MP3 files found.")

    @commands.command(aliases=["git"], pass_context=True)
    async def leave(self, ctx):
        if ctx.voice_client is None:
            await ctx.send("I am not in a voice channel.")
            return

        await ctx.voice_client.disconnect()
        await ctx.send("Left voice channel.")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Troll(bot)) # add the cog to the bot