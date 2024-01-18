import discord, typing, asyncio, requests, io, os
from discord import app_commands
from discord.ext import commands

class Clone(commands.GroupCog, name="clone"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="structure", description="Copy things from other servers. Bot must be in target server.")
    @app_commands.describe(serverid="Target Server ID", mode="Clone mode")
    async def structure(self, interaction: discord.Interaction, serverid: str, mode: typing.Literal["replace", "add"]):
    
        guild = self.bot.get_guild(int(serverid))
        
        if guild is None:
            embed = discord.Embed(title="❌ Error", description="Guild not found", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return
        

        if mode == "replace":
            embed = discord.Embed(title="⚠️ Are you sure you want to proceed?", description="This process will delete **EVERY** channel and category from the server.", color=discord.Color.yellow())
            embed.set_footer(text="Please proceed with 'y' or 'n'.")
            await interaction.channel.send(embed=embed)
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                message = await self.bot.wait_for('message', check=check, timeout=20) 
                if str(message.content).lower() == "y":
                    embed = discord.Embed(title="✅", description="Very well, I will now proceed. This may take a minute.", color=discord.Color.green())
                    await interaction.channel.send(embed=embed)
                elif str(message.content).lower() == "n":
                    embed = discord.Embed(title="❌", description="Very well, I will cancel the operation.", color=discord.Color.red())
                    await interaction.channel.send(embed=embed)
                    return
                else:
                    embed = discord.Embed(title="❌", description="Invalid response.", color=discord.Color.red())
                    await interaction.channel.send(embed=embed)
                    return
            except asyncio.TimeoutError:
                embed = discord.Embed(title="❌", description="You took too long to respond.", color=discord.Color.red())
                await interaction.send(embed=embed)
        

            try:
                for channel in interaction.guild.channels:
                    await channel.delete()
                    
            except Exception as e:
                embed = discord.Embed(title="❌", description="A channel couldn't be deleted.", color=discord.Color.red())
                embed.add_field(name=f"```{e}```")
                await interaction.channel.send(embed=embed)
                return
        
        elif mode == "add":
            embed = discord.Embed(title="<:settingssliders:1196698681869615196> Starting Process", description="This may take a while.", color=discord.Color.yellow())
            await interaction.channel.send(embed=embed)

        try:
            failed = 0
            exchange = {}

            
            if guild.categories:
                for category in guild.categories:
                    await interaction.guild.create_category(category.name)
                    exchange[category.name] = discord.utils.get(interaction.guild.categories, name=category.name)


            for channels in guild.channels:
                if isinstance(channels, discord.TextChannel):
                    if channels.category:
                        try:
                            await interaction.guild.create_text_channel(channels.name, category=exchange[channels.category.name])
                        except:
                            failed += 1
                            pass
                
                    else:
                        try:
                            await interaction.guild.create_text_channel(channels.name)
                        except:
                            failed += 1
                            pass
                elif isinstance(channels, discord.VoiceChannel):
                    if channels.category:
                        try:
                            await interaction.guild.create_voice_channel(channels.name, category=exchange[channels.category.name])
                        except:
                            failed += 1
                            pass
                    else:
                        try:
                            await interaction.guild.create_voice_channel(channels.name)
                        except:
                            failed += 1
                            pass
                
            try:
                
                channel = interaction.guild.text_channels[0]
                embed = discord.Embed(title="✅ Success", description=f"Sucessfully cloned server `{guild.name}`.\nFailed actions: `{failed}`\nMode: `{mode}`", color=discord.Color.green())
                await channel.send(embed=embed)
            except:
                print("failed to send messaage", failed)
                
        except Exception as e:
            print(e)

    
    @app_commands.command(name="emoji", description="Copy emojis from another server")
    @app_commands.describe(serverid="Target Server ID", mode="Clone mode")
    async def emoji(self, interaction: discord.Interaction, serverid: str, mode: typing.Literal["replace", "add"]):
   
        guild = self.bot.get_guild(int(serverid))
        
        if guild is None:
            embed = discord.Embed(title="❌ Error", description="Guild not found", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return
        

        if not guild.emojis:
            embed = discord.Embed(title="❌", description=f"No emojis in {guild.name}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        
        if mode == "replace":
            embed = discord.Embed(title="⚠️ Are you sure you want to proceed?", description="This process will delete **EVERY** emoji from the server.", color=discord.Color.yellow())
            embed.set_footer(text="Please proceed with 'y' or 'n'.")
            await interaction.channel.send(embed=embed)
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                message = await self.bot.wait_for('message', check=check, timeout=20) 
                if str(message.content).lower() == "y":
                    embed = discord.Embed(title="✅", description="Very well, I will now proceed. This may take a minute.", color=discord.Color.green())
                    await interaction.channel.send(embed=embed)
                elif str(message.content).lower() == "n":
                    embed = discord.Embed(title="❌", description="Very well, I will cancel the operation.", color=discord.Color.red())
                    await interaction.channel.send(embed=embed)
                    return
                else:
                    embed = discord.Embed(title="❌", description="Invalid response.", color=discord.Color.red())
                    await interaction.channel.send(embed=embed)
                    return
            except asyncio.TimeoutError:
                embed = discord.Embed(title="❌", description="You took too long to respond.", color=discord.Color.red())
                await interaction.send(embed=embed)
        

            for emoji in interaction.guild.emojis:
                try:
                    await emoji.delete()
                    
                except Exception as e: 
                    embed = discord.Embed(title="❌", description="An emoji couldn't be deleted.", color=discord.Color.red())
                    embed.add_field(name=f"```{e}```")
                    await interaction.channel.send(embed=embed)
                    pass
                
        elif mode == "add":
            embed = discord.Embed(title="⚙️ Starting Process", description="This may take a while.", color=discord.Color.yellow())
            await interaction.channel.send(embed=embed)

        failed = 0
        sucess = 0
        
        for emoji in guild.emojis:
            try:
                response = requests.get(emoji.url)
                image = io.BytesIO(response.content)
                
            
                file_extension = os.path.splitext(emoji.url)[1].lower()
                if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
                    raise ValueError("Unsupported image format")
                
                await interaction.guild.create_custom_emoji(name=emoji.name, image=image.read())
                sucess += 1
            except discord.Forbidden:
                embed = discord.Embed(title="❌", description=f"I don't have permissions.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return
            except (discord.HTTPException, ValueError):
                failed += 1
                embed = discord.Embed(title="❌", description=f"Failed to upload emote: {emoji.name}", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                continue
        
        embed = discord.Embed(title="✅ Success", description=f"", color=discord.Color.green())
        embed.add_field(name="⭐", value=f"Successfully uploaded `{sucess}` emojis.", inline=False)
        embed.add_field(name="❌", value=f"Failed to upload `{failed}` emojis.", inline=False)
        embed.add_field(name="Success rate", value=f"`{(sucess) / len(guild.emojis) * 100}%`", inline=False)
        await interaction.channel.send(embed=embed)



    @app_commands.command(name="roles", description="Clone roles")
    @app_commands.describe(serverid="Target Server ID", mode="Clone mode", ignore_bot_managed_roles="Ignore bot managed roles")
    async def roles(self, interaction: discord.Interaction, serverid: str, mode: typing.Literal["replace", "add"], ignore_bot_managed_roles: bool = False): 

        guild = self.bot.get_guild(int(serverid))
        
        if guild is None:
            embed = discord.Embed(title="❌ Error", description="Guild not found", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return
        

        if mode == "replace":
            embed = discord.Embed(title="⚠️ Are you sure you want to proceed?", description="This process will delete **EVERY** role from the server.", color=discord.Color.yellow())
            embed.set_footer(text="Please proceed with 'y' or 'n'.")
            await interaction.channel.send(embed=embed)
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                message = await self.bot.wait_for('message', check=check, timeout=20) 
                if str(message.content).lower() == "y":
                    embed = discord.Embed(title="✅", description="Very well, I will now proceed. This may take a minute.", color=discord.Color.green())
                    await interaction.channel.send(embed=embed)
                elif str(message.content).lower() == "n":
                    embed = discord.Embed(title="❌", description="Very well, I will cancel the operation.", color=discord.Color.red())
                    await interaction.channel.send(embed=embed)
                    return
                else:
                    embed = discord.Embed(title="❌", description="Invalid response.", color=discord.Color.red())
                    await interaction.channel.send(embed=embed)
                    return
            except asyncio.TimeoutError:
                embed = discord.Embed(title="❌", description="You took too long to respond.", color=discord.Color.red())
                await interaction.send(embed=embed)

            for role in interaction.guild.roles:
                try:
                    if not role.is_bot_managed():
                        await role.delete()
                    
                except Exception as e: 
                    embed = discord.Embed(title="❌", description="A role couldn't be deleted.", color=discord.Color.red())
                    embed.add_field(name=f"```{e}```", value="Please try again.")
                    await interaction.channel.send(embed=embed)
                    pass

        elif mode == "add":
            embed = discord.Embed(title="⚙️ Starting Process", description="This may take a while.", color=discord.Color.yellow())
            await interaction.channel.send(embed=embed)

        failed = 0
        sucess = 0
        for role in guild.roles:
            try:
                if ignore_bot_managed_roles:
                    if not role.is_bot_managed():
                        await interaction.guild.create_role(name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable)
                        sucess += 1
                    else:
                        pass
                else:
                    await interaction.guild.create_role(name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable)
                    sucess += 1
            except discord.Forbidden:
                embed = discord.Embed(title="❌", description=f"I don't have permissions.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return
            except discord.HTTPException:
                failed += 1
                embed = discord.Embed(title="❌", description=f"Failed to create role: {role.name}", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                continue
        
        embed = discord.Embed(title="✅ Success", description=f"", color=discord.Color.green())
        embed.add_field(name="⭐", value=f"Successfully created `{sucess}` roles.", inline=False)
        embed.add_field(name="❌", value=f"Failed to create `{failed}` roles.", inline=False)
        embed.add_field(name="Success rate", value=f"`{sucess / len(guild.roles) * 100}%`", inline=False)
        await interaction.channel.send(embed=embed)



     

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Clone(bot))