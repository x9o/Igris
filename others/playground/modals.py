import discord
from discord.ext import commands
from discord import app_commands

class ModalExample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embedCount = None

    class XModal(discord.ui.Modal, title="Make an embed"):
        emtitle = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="Embed title",
            required=True,
            placeholder="Give your embed a title"
        )

        colour = discord.ui.TextInput(
            
            style=discord.TextStyle.short,
            label="Embed colour",
            required=True,
            placeholder="Give your embed a colour"
        )

        firstfield = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            label="First embed field text",
            required=True,
            max_length=100,
            placeholder="First embed field text"
        )

        firstfieldvalue = discord.ui.TextInput(
            
            style=discord.TextStyle.paragraph,
            label="First embed field value",
            required=True,
            max_length=100,
            placeholder="First embed field value"
        )
        

        async def on_submit(self, interaction: discord.Interaction):
            channel = interaction.guild.get_channel(1195997400704241734)
            await channel.send("hi")

        async def on_error(self, interaction: discord.Interaction, error):
            pass

    @app_commands.command()
    @app_commands.describe(fields="Amount of fields")
    async def embedmaker(self, interaction: discord.Interaction, fields: int):
        modal = ModalExample.XModal()
        self.embedCount = fields
        await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(ModalExample(bot))
