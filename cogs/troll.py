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

######################################################################################
# Helper functions
######################################################################################

    def get_random_mp3(self):
        """Returns the full path of a randomly chosen MP3 file from the directory."""
        if os.path.exists(self.directory) and os.path.isdir(self.directory):
            files = os.listdir(self.directory)
            mp3_files = [file for file in files if file.endswith('.mp3')]
            if mp3_files:
                chosen_file = random.choice(mp3_files)
                return os.path.join(self.directory, chosen_file)
        return None
    
    def get_random_mp3_from_subdirectory(self, subdirectory):
        """Returns the full path of a randomly chosen MP3 file from a specified subdirectory."""
        directory_path = os.path.join('audio', subdirectory)  # Path to the specific subdirectory
        if os.path.exists(directory_path) and os.path.isdir(directory_path):            
            files = os.listdir(directory_path)
            mp3_files = [file for file in files if file.endswith('.mp3')]
            if mp3_files:
                chosen_file = random.choice(mp3_files)
                return os.path.join(directory_path, chosen_file)
        return None

######################################################################################
# Commands
######################################################################################

    @discord.slash_command(name="gel", 
                           description="Joins the voice channel.", 
                           pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.respond("You are not in a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
        await ctx.respond(f"Joined {voice_channel}")

    @discord.slash_command(name="git", 
                           description="Leaves the voice channel.", 
                           pass_context=True)
    async def leave(self, ctx):
        if ctx.voice_client is None:
            await ctx.respond("I am not in a voice channel.")
            return

        await ctx.voice_client.disconnect()
        await ctx.respond("Left voice channel.")

    @discord.slash_command(name="oynat", 
                           description="Plays a random sound file from the selected person.", 
                           pass_context=True)
    async def play(
        self, 
        ctx: discord.ApplicationContext,
        name: discord.Option(str, "Choose a name", choices=["Berkay", "Sarp", "Kerem", "Aras", "Alphan", "Murat"])
        ):

        # Check if the bot is already connected to a voice channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None:
            await ctx.respond("I am not in a voice channel.")
            return
        
        # Check if already playing audio
        if voice_client.is_playing():
            await ctx.respond("I am already playing audio.")
            return

        # Get a random audio file from the selected directory
        audio_path = self.get_random_mp3_from_subdirectory(name.lower())
        if audio_path:
            # Respond back with the path or play the audio file, depending on your use case
            await ctx.respond(f"Playing audio from: {audio_path}")
            source = FFmpegPCMAudio(audio_path)
            ctx.voice_client.play(source)
        else:
            await ctx.respond("No audio files found in the selected directory.")

    @discord.slash_command(name="rulet", description="Disconnect a random user from your current voice channel.")
    @commands.has_permissions(manage_channels=True)
    async def disconnect_random(self, ctx: discord.ApplicationContext):
        # Check if the user invoking the command is in a voice channel
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            members = channel.members
            
            # Check if there are other members in the channel
            if len(members) > 1:
                # Exclude the command user from the list to avoid disconnecting themselves
                # members = [member for member in members if member != ctx.author]
                if members:
                    # Choose a random member to disconnect
                    member_to_disconnect = random.choice(members)
                    await member_to_disconnect.move_to(None)
                    await ctx.respond(f"Randomly disconnected {member_to_disconnect.display_name} from the voice channel.")
                else:
                    await ctx.respond("There are no other members to disconnect in this voice channel.")
            else:
                await ctx.respond("You are alone in the voice channel.")
        else:
            await ctx.respond("You are not currently in any voice channel.")

######################################################################################
# Setup
######################################################################################

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Troll(bot)) # add the cog to the bot