import discord
from discord.ext import commands

class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("This command is not supported.")
        else:
            # Optionally, handle other kinds of errors or pass them up
            # This prevents the handling of the error by any global error handler
            if not isinstance(error, commands.CommandInvokeError):
                return
            # Print the error to the console or log it
            print(f"An error occurred: {error}")

def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))