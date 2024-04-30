import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_ready(self):
        print("Cog - Ping is loaded.")

    @commands.command(aliases=["latency"])
    async def ping(self, ctx):
        bot_latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! {bot_latency}ms")

def setup(bot):
    bot.add_cog(Ping(bot))