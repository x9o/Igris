import discord 
from discord.ext import commands
from data.config import TOKEN, TESTTOKEN

igris = commands.Bot(command_prefix="i.", intents=discord.Intents.all())

initial_Cogs = ["cogs.protection", "cogs.misc", "cogs.clone", "cogs.info", "cogs.logger"]

@igris.event
async def on_ready():
    for cog in initial_Cogs:
        await igris.load_extension(cog)
    await igris.tree.sync()
    print(f"Logged in as {igris.user}")
    await igris.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Just playing around"))
    

igris.run(token=TOKEN)