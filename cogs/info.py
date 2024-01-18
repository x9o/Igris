import discord
from discord.ext import commands
from discord import app_commands

class InfoCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.version = "0.1"

    @app_commands.command(name="about", description="Get information about Igris")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(title="About", color=discord.Color.dark_purple())
        embed.set_author(name="Igris", icon_url="https://images-ext-2.discordapp.net/external/RwX2S-scd50PynXg8Ao2ztMLhGyU-APDtaSK4heUQu4/%3Fsize%3D512/https/cdn.discordapp.com/avatars/999232775443984495/e891cb41a5acf438a4ec1ef1e31477b5.png?format=webp&quality=lossless&width=655&height=655")
        embed.add_field(name="<:share:1196671990807924796> Version", value=f"`{self.version}`", inline=False)
        embed.add_field(name="<:rocketlunch:1196671535436537917> What is igris?", value="```Igris is a utility, security and a watcher bot created with discord.py```", inline=False)
        embed.add_field(name="<:interrogation:1196671833945157744> Who is igris named after?", value="```Igris is named a character in Solo Leveling.```", inline=False)
        embed.add_field(name="<:user:1196671338476212244> Developer", value="<:github:1168890688943968256> x9o\n<:bithub:1168916836704858253> x0lo", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Get invite link for Igris")
    async def invite(self, interaction: discord.Interaction):
        embed = discord.Embed(title="<:share:1196671990807924796> Invite", color=discord.Color.dark_purple())
        embed.set_author(name="Igris", icon_url="https://images-ext-2.discordapp.net/external/RwX2S-scd50PynXg8Ao2ztMLhGyU-APDtaSK4heUQu4/%3Fsize%3D512/https/cdn.discordapp.com/avatars/999232775443984495/e891cb41a5acf438a4ec1ef1e31477b5.png?format=webp&quality=lossless&width=655&height=655")
        embed.add_field(name="", value="<:lilacflame:1196707654672846908> [Arise](https://discord.com/api/oauth2/authorize?client_id=999232775443984495&permissions=8&scope=bot) <:lilacflame:1196707654672846908>", inline=False)

        await interaction.response.send_message(embed=embed)

    

        
    

async def setup(bot):
    await bot.add_cog(InfoCogs(bot))