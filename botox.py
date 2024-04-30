######################################################################################
# Imports
######################################################################################
import discord
from discord.ext import commands, tasks

from config import *
from apikeys import *

import os
import datetime
from enum import Enum

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(debug_guilds=[GUILD_ID], 
                   command_prefix="!", 
                   intents=intents)

connections = {}

'''
class Sinks(Enum):
    mp3 = discord.sinks.MP3Sink()
    wav = discord.sinks.WaveSink()
    pcm = discord.sinks.PCMSink()
    ogg = discord.sinks.OGGSink()
    mka = discord.sinks.MKASink()
    mkv = discord.sinks.MKVSink()
    mp4 = discord.sinks.MP4Sink()
    m4a = discord.sinks.M4ASink()
'''


######################################################################################
# Helper functions
######################################################################################

# Load all cogs in the cogs directory
def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

# Check if a member ID is in the members dictionary
def check_member_id(member_id_to_check, members):
    if member_id_to_check in members:
        return True, members[member_id_to_check]
    else:
        return False, None

def check_filename(filename, members):
    # Remove the extension from the filename to get the ID
    member_id_to_check = os.path.splitext(filename)[0]
    
    # Convert to int if your IDs are integers and the filename is supposed to contain only the ID
    try:
        member_id_to_check = int(member_id_to_check)
    except ValueError:
        return False, None  # or handle the error as appropriate

    # Check the ID in the dictionary
    if member_id_to_check in members:
        return True, members[member_id_to_check]
    else:
        return False, None

def save_recordings(files, members):
    # Create the directory path
    for file in files:
        
        print(f"File: {file.filename}")
        # Check if the member ID is in the members dictionary
        found, name = check_filename(file.filename, members)
        if not found:
            print(f"Member ID {file.filename} not found in the members dictionary.")
            continue
        
        directory_path = f'recordings/{name}'

        # Ensure the directory exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory created: {directory_path}")

        # Format the current time in a filename-friendly format (e.g., YYYYMMDD-HHMMSS)
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

        # Create the filename with the timestamp
        filename = f"{timestamp}.wav"

        # Full path for the file
        file_path = os.path.join(directory_path, filename)
        print("saving")
        # Assuming recording_data is binary data of the recording
        with open(file_path, 'wb') as f:
            f.write(file.fp.read())

        print(f"Recording saved to {file_path}")

######################################################################################
# Callbacks
######################################################################################

# Callback function that is called when the recording is finished
async def finished_callback(sink, channel: discord.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()
    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]

    print("finished_callback")

    save_recordings(files, members)
  
    # await channel.send( f"Finished! Recorded audio for {', '.join(recorded_users)}.",
    #                         files=files)

######################################################################################
# Event handlers
######################################################################################

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")

# Event handler for when a member joins or leaves a voice channel
@bot.event
async def on_voice_state_update(member, before, after):

    # Check if the member is the bot itself or the person of interest
    if member.id == bot.user.id or member.id!=person_of_interest:
        return

    # Check if the member left a voice channel
    if before.channel is not None and after.channel is None:
        print(f"{member} left {before.channel}")

        # Check if the bot is already connected to a voice channel
        voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)

        if voice_client is not None:
            # Disconnect the bot from the voice channel
            await voice_client.disconnect()

    # Check if the member joined a voice channel
    elif after.channel is not None:
        print(f"{member} with id {member.id} joined {after.channel}")        
        
        # Check if the bot is already connected to a voice channel
        voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
            
        if voice_client is None:
            # Connect the bot to the member's new channel
            await after.channel.connect()
        else:
            # Move the bot to the new channel
            await voice_client.move_to(after.channel)

            #print("try play spound")
            # Play an audio file if the bot is not already playing audio
            # voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)

            #source = FFmpegPCMAudio("audio/kerem-laugh.mp3")
            #voice_client.play(source)

######################################################################################
# Commands
######################################################################################

@bot.slash_command()
async def start(ctx: discord.ApplicationContext):
    """Record your voice!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    print("You are in a voice channel")

    # Get the guild's voice client if it exists
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if vc and vc.is_connected():
        # Check if it's connected to the right channel
        if vc.channel != voice.channel:
            print("Bot is connected to a different voice channel. Reconnecting...")
            await vc.move_to(voice.channel)
    else:
        # Connect to the voice channel since the bot is not yet connected or not connected to the right channel
        print("Bot is trying to connect to the voice channel.")
        vc = await voice.channel.connect()

    connections[ctx.guild.id] = vc  # Store or update the current voice client

    sink = discord.sinks.WaveSink()

    vc.start_recording(sink, lambda sink: finished_callback(sink, ctx.channel))

    await ctx.respond("The recording has started!")

@bot.slash_command()
async def stop(ctx: discord.ApplicationContext):
    """Stop recording."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")

######################################################################################
# Run the bot
######################################################################################
load_cogs()
bot.run(BOT_TOKEN)