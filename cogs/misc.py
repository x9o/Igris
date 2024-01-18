import discord, chat_exporter, io, requests, os, re, zipfile, asyncio
from discord import app_commands
from discord.ext import commands
from utils.utils import Info

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Get the bot's ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```{round(self.bot.latency * 1000)}ms```")

    @app_commands.command(name="exportchat", description="Powered by mahtoid/DiscordChatExporterPy")
    @app_commands.describe(messagelimit="The number of messages to export.", timezone="The timezone to use for the timestamp.", military_time="Use 24-hour time format.")
    async def exportchat(self, interaction: discord.Interaction, messagelimit: int = 100, timezone: str = "UTC", military_time: bool = True):
        transcript = await chat_exporter.export(
            interaction.channel,
            limit=messagelimit,
            tz_info=timezone,
            military_time=military_time,
            bot=self.bot,
        )

        if transcript is None:
            return

        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html",
        )
         
        
        await interaction.response.send_message(file=transcript_file)

    @app_commands.command(name="ip", description="Get information from an IP address")
    @app_commands.describe(ip_address="IP address you want to lookup.")
    async def ip(self, interaction: discord.Interaction, ip_address: str):
        ipx = Info.ipinfo(ip_address)

        if ipx == "❌ Invalid IP/Error.":
            embed = discord.Embed(title="❌ Error", description="Invalid IP", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f'{ip_address}', color=discord.Color.dark_gold())
            embed.add_field(name='🌍 Country', value=f'{ipx[0]}', inline=True)
            embed.add_field(name='🌆 City', value=f'{ipx[1]}', inline=True)
            embed.add_field(name='🌳 Region', value=f'{ipx[11]}', inline=True)
            embed.add_field(name='🤐 Zip Code', value=f'{ipx[2]}', inline=True)
            embed.add_field(name='🅰️ ASN', value=f'{ipx[10]}', inline=True)
            embed.add_field(name=':information_source: ISP', value=f'{ipx[3]}', inline=True)
            embed.add_field(name='🕝 Timezone', value=f'{ipx[4]}', inline=True)
            embed.add_field(name='📏 Latitude', value=f'    {ipx[5]}', inline=True)
            embed.add_field(name='📐 Longtitude', value=f'{ipx[6]}', inline=True)
            embed.add_field(name='🌐 Geolocation', value=f'{ipx[7]}', inline=True)
            embed.add_field(name='🥸 Hostname', value=f'{ipx[8]}', inline=True)
            embed.add_field(name='🦾 Proxy', value=f'{ipx[9]}', inline=True)
            
 
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="github", description="Get information from a Github profile")
    @app_commands.describe(user="Github username")
    async def github(self, interaction: discord.Interaction, user: str):
        response = requests.get(f"https://api.github.com/users/{user}")

        if response.status_code == 200:
            profile_data = response.json()
            name = profile_data['name']
            bio = profile_data['bio']
            followers = profile_data['followers']
            following = profile_data['following']
            avatar_url = profile_data['avatar_url']

            repo_response = requests.get(f"https://api.github.com/users/{user}/repos")

            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                x = user

                embed = discord.Embed(title=f'{x}', color=discord.Color.green())
                embed.set_thumbnail(url=avatar_url)
                embed.add_field(name='📂 Profile', value=f'https://github.com/{x}', inline=False)
                embed.add_field(name='🏷️ Name', value=f'{name}', inline=False)
                embed.add_field(name='💬 Bio', value=f'{bio}', inline=False)
                embed.add_field(name=':baby: Followers', value=f'[{followers}](https://github.com/{x}?tab=followers)', inline=False)
                embed.add_field(name='🥸 Following', value=f'[{following}](https://github.com/{x}?tab=following)', inline=False)
                embed.add_field(name='📖 Public repositories:', value='', inline=False)
                embed.set_footer(text="Github: x9o")

                for repo in repo_data:
                    repo_name = repo['name']
                    repo_url = repo['html_url']
                    stars = repo['stargazers_count'] 
                    forks = repo['forks_count']  
                    embed.add_field(name=repo_name, value=f'⭐ Stars: {stars}\n🍴 Forks: {forks}\n{repo_url}', inline=False)

                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(title="❌ Error", description="Failed to retrieve repository information.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="❌ Error", description="Failed to retrieve profile information.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)


    @app_commands.command(name="mass_upload_emojis", description="Takes a zip file and uploads all of the images as emojis to the server")
    @app_commands.describe(file="Zip file")
    async def mass_upload_emojis(self, interaction: discord.Interaction, file: discord.Attachment):
        
        attachment = file
        if not attachment.filename.endswith('.zip'):
            embed = discord.Embed(title="❌ Invalid file format", description="Please upload a zip file.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        

        embed = discord.Embed(title="<:rocketlunch:1196671535436537917> Uploading emojis...", description="", color=discord.Color.dark_purple())
        await interaction.response.send_message(embed=embed)
        zip_data = io.BytesIO(await attachment.read())

        failed = 0
        total = 0
        sucess = 0

        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.gif'):
                    emoji_data = zip_ref.read(filename)
                    emoji_name = os.path.splitext(filename)[0]
                    emoji_name = re.sub(r'[^a-zA-Z0-9_]', '', emoji_name)  
                
                    try:
                        await interaction.guild.create_custom_emoji(name=emoji_name, image=emoji_data)
                        await asyncio.sleep(0.8)
                        total += 1
                        sucess += 1
                    except Exception as e:
                        total += 1
                        failed += 1
                        embed = discord.Embed(title=f"❌ Failed to create emoji '{emoji_name}'", description="", color=discord.Color.red())
                        embed.add_field(name=f"Error", value=f"```{str(e)}```")
                        await interaction.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"❌ `{filename}` is not an image or gif.", description="This file will be ignored", color=discord.Color.red())
                    await interaction.channel.send(embed=embed)
                    continue
                    


        success_rate = sucess / total * 100 if total > 0 else 0
        embed = discord.Embed(title=f"✅ `{sucess}` emojis uploaded", description=f"Success rate: ```{success_rate:.2f}%```", color=discord.Color.green())
        await interaction.channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Misc(bot))