import discord
from discord.ext import commands, tasks
import os
import datetime
from enum import Enum
import asyncio

from config import *

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

class Record(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
        self.connections = {}  # Moved the connections dictionary inside the cog

    @commands.Cog.listener() 
    async def on_ready(self):
        print("Cog - Record is loaded.")

    ######################################################################################
    # Helper functions
    ######################################################################################

    # Utility to check and manage filenames and directory creation
    def check_filename(self, filename, members):
        member_id_to_check = os.path.splitext(filename)[0]
        try:
            member_id_to_check = int(member_id_to_check)
        except ValueError:
            return False, None

        return (True, members[member_id_to_check]) if member_id_to_check in members else (False, None)

    def save_recordings(self, files, members):
        for file in files:
            found, name = self.check_filename(file.filename, members)
            if not found:
                continue

            directory_path = f'recordings/{name}'
            os.makedirs(directory_path, exist_ok=True)
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            filename = f"{timestamp}.wav"
            file_path = os.path.join(directory_path, filename)

            with open(file_path, 'wb') as f:
                f.write(file.fp.read())

    ######################################################################################
    # Callbacks
    ######################################################################################

    # Callback function for recording completion
    async def finished_callback(self, sink, channel):
        recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
        await sink.vc.disconnect()

        files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
        self.save_recordings(files, members)
        #await channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files)

    ######################################################################################
    # Commands
    ######################################################################################

    # Commands to manage recording
    # @discord.slash_command(name="kayit_baslat", description="Starts recording the channel.")
    # async def start_recording(self, ctx):
    #     voice = ctx.author.voice
    #     if not voice:
    #         return await ctx.respond("You're not in a vc right now")

    #     vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    #     if vc and vc.is_connected() and vc.channel != voice.channel:
    #         await vc.move_to(voice.channel)
    #     elif not vc:
    #         vc = await voice.channel.connect()

    #     self.connections[ctx.guild.id] = vc
    #     sink = discord.sinks.WaveSink()
    #     vc.start_recording(sink, lambda sink=sink: self.finished_callback(sink, ctx.channel))

    #     await ctx.respond("The recording has started!")

    @discord.slash_command(name="kayit_bitir", description="Stops recording the channel.")
    async def stop_recording(self, ctx):
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            vc.stop_recording()
            del self.connections[ctx.guild.id]
            await ctx.respond("Recording stopped.")
        else:
            await ctx.respond("Not recording in this guild.")

    @discord.slash_command(name="kayit_baslat", description="Starts recording the channel for 10 minutes.")
    async def start_recording_10mins(self, ctx):
        voice = ctx.author.voice
        if not voice:
            return await ctx.respond("You're not in a voice channel right now.")
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc and vc.is_connected() and vc.channel != voice.channel:
            await vc.move_to(voice.channel)
        elif not vc:
            vc = await voice.channel.connect()
        
        self.connections[ctx.guild.id] = vc
        sink = discord.sinks.WaveSink()
        vc.start_recording(sink, lambda sink=sink: self.finished_callback(sink, ctx.channel))
        await ctx.respond("Recording has started for 10 minutes.")

        # Wait for 10 minutes before stopping the recording
        await asyncio.sleep(600)  # 600 seconds equals 10 minutes
        if vc and vc.recording:
            vc.stop_recording()
            await ctx.followup.send("Recording stopped after 10 minutes.")


######################################################################################
# Setup
######################################################################################

def setup(bot):
    bot.add_cog(Record(bot))
