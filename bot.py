import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
intents = discord.Intents.default()
intents.members = True
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix='s!',intents=intents)
@client.event
async def on_ready():
    print("Sentient Medbay Scanner is analysing. Hello.")
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("Among Us")
    )
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Please give all the arguments.")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send("Conversion of arguments failed.")
    elif isinstance(error,commands.errors.CommandNotFound):
        await ctx.send("Command not found.")
    elif isinstance(error, commands.errors.NotOwner):
        await ctx.send("You ain't the bot owner!")
    print(f"ERROR: {error}")
client.load_extension("cogs.main")
client.load_extension("cogs.admin")
client.run(token)
