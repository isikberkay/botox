######################################################################################
# Imports
######################################################################################
import discord
from discord.ext import commands, tasks

from config import *
from apikeys import *

import os
import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(debug_guilds=[GUILD_ID], 
                   command_prefix="!", 
                   intents=intents)


######################################################################################
# Helper functions
######################################################################################

# Load all cogs in the cogs directory
def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")


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

######################################################################################
# Commands
######################################################################################



######################################################################################
# Run the bot
######################################################################################
load_cogs()
bot.run(BOT_TOKEN)