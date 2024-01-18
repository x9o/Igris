import discord, typing, time, asyncio
from discord import app_commands
from discord.ext import commands
from utils.utils import Time
from datetime import timedelta


class Protect(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        

        self.spam_antispam: bool = False
        self.spam_threshold: int = 6
        self.spam_timeframe: int = 3
        self.spam_detection: dict = {}
        self.spam_action: str = "message"
        self.spam_timeoutlength = timedelta(seconds=60)

        
        self.massroledelete_toggle: bool = False
        self.massroledelete_threshold: int = 5
        self.massroledelete_timerange: int = 3
        self.massroledelete_deletion_tracker: dict = {}
        self.massroledelete_message_sent: dict = {} 


        self.masschanneldelete_toggle: bool = False
        self.masschanneldelete_threshold: int = 5
        self.masschanneldelete_timerange: int = 3
        self.masschanneldelete_deletion_tracker: dict = {}
        self.masschanneldelete_message_sent: dict = {}

        self.massping_toggle: bool = False
        self.massping_action: str = "message"
        self.massping_timeoutduration = timedelta(minutes=30)
        self.massping_threshold: int = 5
        self.massping_supress: bool = True
        
        self.massban_toggle: bool = False
        self.massban_threshold: int = 3
        self.massban_timerange: int = 3  
        self.massban_deletion_tracker: dict = {}
        self.massban_message_sent: dict = {}


    def MassPingCheck(self, message):
        print(len(message.mentions))
        if len(message.mentions) >= self.massping_threshold:
            return True
    
        

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)

        if self.massping_toggle:
            if self.MassPingCheck(message):
                if self.massping_supress:
                    await message.delete()
                if self.massping_action == "message":
                    embed = discord.Embed(title="⚠️ Mass ping detected", description=f"{message.author.mention}", color=discord.Color.red())
                    await message.channel.send(embed=embed)
                elif self.massping_action == "timeout":
                    await message.author.timeout(self.massping_timeoutduration)
                    embed = discord.Embed(title="⚠️ Mass ping detected", description=f"Timed out {message.author.mention} for `{Time.format_timedelta(self.massping_timeoutduration)}`", color=discord.Color.red())
                    await message.channel.send(embed=embed)
                elif self.massping_action == "kick":
                    await message.author.kick(reason="Mass ping detected")
                    embed = discord.Embed(title="⚠️ Mass ping detected", description=f"Kicked {message.author.mention}", color=discord.Color.red())
                    await message.channel.send(embed=embed)

        


        if self.spam_antispam:
            if message.author.id in self.spam_detection:
                user_data = self.spam_detection[message.author.id]
                user_data['message_count'] += 1

                
                if user_data['message_count'] >= self.spam_threshold:
                    
                    time_difference = message.created_at - user_data['first_message_time']
                    if time_difference.total_seconds() <= self.spam_timeframe:
                        
                        if self.spam_action == "message":
                            embed = discord.Embed(title="⚠️ Spam detected", description=f"{message.author.mention}", color=discord.Color.red())
                            await message.channel.send(embed=embed)
                        elif self.spam_action == "timeout":
                            embed = discord.Embed(title="⚠️ Spam detected", description=f"Timed out {message.author.mention} for {Time.format_timedelta(self.spam_timeoutlength)}", color=discord.Color.red())
                            await message.author.timeout(self.spam_timeoutlength)
                            await message.channel.send(embed=embed)
                        elif self.spam_action == "kick":
                            embed = discord.Embed(title="⚠️ Spam detected", description=f"Kicked {message.author.mention}.", color=discord.Color.red())
                            await message.author.kick()
                            await message.channel.send(embed=embed)
                        
                
                if time_difference.total_seconds() > self.spam_timeframe:
                    user_data['message_count'] = 1
                    user_data['first_message_time'] = message.created_at

            else:
                
                self.spam_detection[message.author.id] = {
                    'message_count': 1,
                    'first_message_time': message.created_at
                }

    # finished!
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        

        guild = role.guild
        current_time = time.time()

        if guild.id not in self.massroledelete_deletion_tracker:
            self.massroledelete_deletion_tracker[guild.id] = {"count": 1, "time": current_time, "deleted_roles": []}

        else:
            if current_time - self.massroledelete_deletion_tracker[guild.id]["time"] > self.massroledelete_timerange:
                self.massroledelete_deletion_tracker[guild.id] = {"count": 1, "time": current_time, "deleted_roles": []}
                self.massroledelete_deletion_tracker[guild.id]["deleted_roles"].append(role)
            else:
                self.massroledelete_deletion_tracker[guild.id]["count"] += 1
                self.massroledelete_deletion_tracker[guild.id]["deleted_roles"].append(role)

            if self.massroledelete_deletion_tracker[guild.id]["count"] >= self.massroledelete_threshold:
                self.massroledelete_deletion_tracker[guild.id]["deleted_roles"].append(role)
                async for entry in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
                    user = entry.user
                    if not self.massroledelete_message_sent.get(user): # Check if the user has been tackled
                        self.massroledelete_message_sent[user] = True
                        try:
                            if user.bot:
                                await user.ban(reason="Mass role deletion detected")
                                keyword = "banned"
        
                            else:
                                await user.edit(roles=[])
                                await user.timeout(timedelta(days=1))
                                keyword = "quarantined"

                            
                            embed = discord.Embed(title=f":warning: Mass role deletion detected", description=f":white_check_mark: Successfully {keyword} {user.mention}", color=discord.Color.green())
                            await guild.text_channels[0].send(embed=embed)
        
                        except Exception as e:
                            embed = discord.Embed(title=f":warning: Mass role deletion detected", description=f":x: Failed to quarantine {user.mention}\nException: ```{e}```", color=discord.Color.red())
                            await guild.text_channels[0].send(embed=embed)
                            
                        embed = discord.Embed(title=f"🔨 Restore `{len(self.massroledelete_deletion_tracker[guild.id]['deleted_roles'])}` roles?", description="```y/n```", color=discord.Color.purple())
                        await guild.text_channels[0].send(embed=embed)
                        
                    
                        def check(m):
                            return m.author.guild_permissions.administrator and m.channel == guild.text_channels[0] and m.content.lower() in ["y", "n"]

                        try:
                            response = await self.bot.wait_for("message", check=check, timeout=60)
                            if response.content.lower() == "y":
                                restored = 0
                                embed = discord.Embed(title=f"⚙️ Restoring `{len(self.massroledelete_deletion_tracker[guild.id]['deleted_roles'])}` mass deleted roles", description="", color=discord.Color.purple())
                                await guild.text_channels[0].send(embed=embed)
                                for role in self.massroledelete_deletion_tracker[guild.id]["deleted_roles"]:
                                    if role is not None:
                                        await guild.create_role(name=role.name, permissions=role.permissions, colour=role.colour, hoist=role.hoist, mentionable=role.mentionable)
                                        restored += 1 

                                await guild.text_channels[0].send(response.author.mention)
                                embed = discord.Embed(title=f"✅ Successfully restored `{len(self.massroledelete_deletion_tracker[guild.id]['deleted_roles'])}` roles", description=f"Sucess rate: `{restored / len(self.massroledelete_deletion_tracker[guild.id]['deleted_roles']) * 100}%`", color=discord.Color.green())
                                await guild.text_channels[0].send(embed=embed)
                                self.massroledelete_deletion_tracker[guild.id]["deleted_roles"] = [] 
                                
                            else:

                                embed = discord.Embed(title=f"⚠️ Mass deleted roles will not be restored.", description="", color=discord.Color.yellow())
                                await guild.text_channels[0].send(embed=embed)

                        
                        except asyncio.TimeoutError:
                            embed = discord.Embed(title=f"⚠️ Interaction timed out", description="Mass deleted channels will not be restored.", color=discord.Color.yellow())
                            await guild.text_channels[0].send(embed=embed)

                    else:
                        print("Embeds already sent! ")

                    
        
        
    # finished!
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = self.bot.get_guild(channel.guild.id)
        current_time = time.time()

        if channel.guild.id not in self.masschanneldelete_deletion_tracker:
            self.masschanneldelete_deletion_tracker[channel.guild.id] = {"count": 1, "time": current_time, "deleted_channels": [channel]}
        else:
            if current_time - self.masschanneldelete_deletion_tracker[channel.guild.id]["time"] > self.masschanneldelete_timerange:
                self.masschanneldelete_deletion_tracker[channel.guild.id] = {"count": 1, "time": current_time, "deleted_channels": [channel]}
            else:
                self.masschanneldelete_deletion_tracker[channel.guild.id]["count"] += 1
                self.masschanneldelete_deletion_tracker[channel.guild.id]["deleted_channels"].append(channel)

            if self.masschanneldelete_deletion_tracker[channel.guild.id]["count"] >= self.masschanneldelete_threshold:
                async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                    user = entry.user
                    if not self.masschanneldelete_message_sent.get(user): # Check if the user has been tackled
                        self.masschanneldelete_message_sent[user] = True
                        try:

                            if user.bot:
                                await user.ban(reason="Mass channel deletion detected")
                                keyword = "banned"

                            else:
                                await user.edit(roles=[])
                                await user.timeout(timedelta(days=1))
                                keyword = "quarantined"

                            embed = discord.Embed(title=f"⚠️ Mass channel deletion detected", description=f"✅ Successfully {keyword} {user.mention}", color=discord.Color.green())
                            await guild.text_channels[0].send(embed=embed)
                        except Exception as e:
                            embed = discord.Embed(title=f"⚠️ Mass channel deletion detected", description=f"❌ Failed to quarantine {user.mention}\nException: ```{e}```", color=discord.Color.red())
                            await guild.text_channels[0].send(embed=embed)

                        embed = discord.Embed(title=f"🔨 Restore `{len(self.masschanneldelete_deletion_tracker[guild.id]['deleted_channels'])}` channels?", description="```y/n```", color=discord.Color.purple())
                        await guild.text_channels[0].send(embed=embed)

                        

                        def check(m):
                            return m.author.guild_permissions.administrator and m.channel == guild.text_channels[0] and m.content.lower() in ["y", "n"]
                        try:
                            response = await self.bot.wait_for("message", check=check, timeout=60)
                            if response.content.lower() == "y":
                                restored = 0
                                embed = discord.Embed(title=f"⚙️ Restoring `{len(self.masschanneldelete_deletion_tracker[guild.id]['deleted_channels'])}` mass deleted channels", description="", color=discord.Color.purple())
                                await guild.text_channels[0].send(embed=embed)
                                for channel in self.masschanneldelete_deletion_tracker[guild.id]["deleted_channels"]:
                                    if channel is not None:
                                        if isinstance(channel, discord.CategoryChannel):
                                            await guild.create_category_channel(name=channel.name, position=channel.position)
                                        else:
                                            await guild.create_text_channel(name=channel.name, position=channel.position, category=channel.category, nsfw=channel.nsfw, slowmode_delay=channel.slowmode_delay, overwrites=channel.overwrites)
                                        restored += 1

                                await guild.text_channels[0].send(response.author.mention)
                                embed = discord.Embed(title=f"✅ Successfully restored `{restored}` channels", description=f"Success rate: `{restored / len(self.masschanneldelete_deletion_tracker[guild.id]['deleted_channels']) * 100}%`", color=discord.Color.green())
                                await guild.text_channels[0].send(embed=embed)
                                self.masschanneldelete_deletion_tracker[guild.id]["deleted_channels"] = []
                            else:
                                embed = discord.Embed(title=f"⚠️ Mass deleted channels will not be restored.", description="", color=discord.Color.yellow())
                                await guild.text_channels[0].send(embed=embed)
                        except asyncio.TimeoutError:
                            embed = discord.Embed(title=f"⚠️ Interaction timed out", description="Mass deleted channels will not be restored.", color=discord.Color.yellow())
                            await guild.text_channels[0].send(embed=embed)
                    else:
                        print("Embeds sent!")

                    

                    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        current_time = time.time()

        if guild.id not in self.massban_deletion_tracker:
            self.massban_deletion_tracker[guild.id] = {"count": 1, "time": current_time, "banned_users": []}
        else:
            if current_time - self.massban_deletion_tracker[guild.id]["time"] > self.massban_timerange:
                self.massban_deletion_tracker[guild.id] = {"count": 1, "time": current_time, "banned_users": []}
                self.massban_deletion_tracker[guild.id]["banned_users"].append(user)
            else:
                self.massban_deletion_tracker[guild.id]["count"] += 1
                self.massban_deletion_tracker[guild.id]["banned_users"].append(user)

            if self.massban_deletion_tracker[guild.id]["count"] >= self.massban_threshold:
                self.massban_deletion_tracker[guild.id]["banned_users"].append(user)
                async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                    culprit = entry.user
                    if not self.massban_message_sent.get(culprit):
                        self.massban_message_sent[culprit] = True
                        try:
                            if culprit.bot:
                                await culprit.ban(reason="Mass ban detected")
                                keyword = "banned"
                            else:
                                await culprit.edit(roles=[])
                                await culprit.timeout(timedelta(days=7))
                                keyword = "quarantined"

                            embed = discord.Embed(
                                title=f"⚠️ Mass ban detected",
                                description=f"✅ Successfully {keyword} {culprit.mention}",
                                color=discord.Color.red()
                            )
                            await guild.text_channels[0].send(embed=embed)

                        except Exception as e:
                            embed = discord.Embed(
                                title=f":warning: Mass ban detected",
                                description=f":x: Failed to quarantine {culprit.mention}\nException: ```{e}```",
                                color=discord.Color.red()
                            )
                            await guild.text_channels[0].send(embed=embed)
        


    @app_commands.command(name="anti_spam", description="Anti spam settings")
    @app_commands.describe(toggle="Enable or disable antispam", threshold="Number of messages within the time frame to trigger spam detection", timeframe="Time frame in seconds", action="Action to take", timeoutduration="Timeout duration")
    async def anti_spam(self, interaction: discord.Interaction, toggle: typing.Literal["enable", "disable"], threshold: int = 6, timeframe: int = 3, action: typing.Literal["timeout", "kick", "message"] = "message", timeoutduration: typing.Literal["60 secs", "5 mins", "10 mins", "1 hour", "1 day", "1 week"] = None):

        if toggle == "enable":
            self.spam_antispam = True
        else:
            self.spam_antispam = False
        if threshold:
            self.spam_threshold = int(threshold)
        if timeframe:
            self.spam_timeframe = int(timeframe)
        if action == "timeout" and timeoutduration:
            self.spam_action = "timeout"
            self.spam_timeoutlength = Time.timedelta_convert(timeoutduration)
        elif action == "kick" and not timeoutduration:
            self.spam_detection = "kick"
        elif action == "message" and not timeoutduration:
            self.spam_action = "message"
        else:
            embed = discord.Embed(title="❌ Invalid settings", description="Invalid settings", color=discord.Color.red())
            interaction.response.send_message(embed=embed)
        

        embed = discord.Embed(title="<:settingssliders:1196698681869615196> Antispam settings", color=discord.Color.dark_purple())
        embed.add_field(name="Status", value=f"```{self.spam_antispam}```", inline=False)
        embed.add_field(name="Threshold", value=f"```{self.spam_threshold}```", inline=False)
        embed.add_field(name="Timeframe", value=f"```{self.spam_timeframe}```", inline=False)
        embed.add_field(name="Action", value=f"```{self.spam_action}```", inline=False)
        embed.add_field(name="Timeout duration", value=f"```{self.spam_timeoutlength if self.spam_action == 'timeout' else 'N/A'}```", inline=False)
        
        await interaction.channel.send(embed=embed)

    @app_commands.command(name="anti_mass_role_delete", description="Anti mass role delete settings")
    @app_commands.describe(toggle="Enable or disable antispam", threshold="Number of messages within the time frame to trigger spam detection", timeframe="Time frame in seconds")
    async def anti_mass_role_delete(self, interaction: discord.Interaction, toggle: typing.Literal["enable", "disable"], threshold: int = 5, timeframe: int = 3):

        if toggle == "enable":
            self.massroledelete_toggle = True
        else:
            self.massroledelete_toggle = False
        if threshold:
            self.massroledelete_threshold = int(threshold)
        if timeframe:
            self.massroledelete_timerange = int(timeframe)

        embed = discord.Embed(title="<:settingssliders:1196698681869615196> Anti mass role delete settings", color=discord.Color.dark_purple())
        embed.add_field(name="Status", value=f"```{self.massroledelete_toggle}```", inline=False)
        embed.add_field(name="Threshold", value=f"```{self.massroledelete_threshold}```", inline=False)
        embed.add_field(name="Timeframe", value=f"```{self.massroledelete_timerange}```", inline=False)
        
        await interaction.channel.send(embed=embed)
            
    @app_commands.command(name="anti_mass_channel_delete", description="Anti mass channel delete settings")
    @app_commands.describe(toggle="Enable or disable antispam", threshold="Number of messages within the time frame to trigger spam detection", timeframe="Time frame in seconds")
    async def anti_mass_channel_delete(self, interaction: discord.Interaction, toggle: typing.Literal["enable", "disable"], threshold: int = 5, timeframe: int = 3):

        if toggle == "enable":
            self.masschanneldelete_toggle = True
        else:
            self.masschanneldelete_toggle = False
        if threshold:
            self.masschanneldelete_threshold = int(threshold)
        if timeframe:
            self.masschanneldelete_timerange = int(timeframe)

        embed = discord.Embed(title="<:settingssliders:1196698681869615196> Anti mass channel delete settings", color=discord.Color.dark_purple())
        embed.add_field(name="Status", value=f"```{self.masschanneldelete_toggle}```", inline=False)
        embed.add_field(name="Threshold", value=f"```{self.masschanneldelete_threshold}```", inline=False)
        embed.add_field(name="Timeframe", value=f"```{self.masschanneldelete_timerange}```", inline=False)
        
        await interaction.channel.send(embed=embed)

    @app_commands.command(name="anti_mass_ping", description="Anti mass ping settings")
    @app_commands.describe(toggle="Enable or disable antispam", threshold = "Number of pings to trigger anti-mass ping",  action="Action to take", supress="Delete the message", timeoutduration="Timeout duration in minutes")
    async def anti_mass_ping(self, interaction: discord.Interaction, toggle: typing.Literal["enable", "disable"], threshold: int = 5, action: typing.Literal["kick", "timeout", "message"] = "message", supress: bool = True, timeoutduration: typing.Literal["60 secs", "5 mins", "10 mins", "1 hour", "1 day", "1 week"] = None):

        if toggle == "enable":
            self.massping_toggle = True
        else:
            self.massping_toggle = False

        self.massping_threshold = threshold

        self.massping_action = action

        self.massping_supress = supress

        if timeoutduration and action == "timeout":
            self.massping_timeoutduration = Time.timedelta_convert(timeoutduration)


        embed = discord.Embed(title="<:settingssliders:1196698681869615196> Anti mass ping settings", color=discord.Color.dark_purple())
        embed.add_field(name="Status", value=f"```{self.massping_toggle}```", inline=False)
        embed.add_field(name="Action", value=f"```{self.massping_action}```", inline=False)
        embed.add_field(name="Threshold", value=f"```{self.massping_threshold}```", inline=False)
        embed.add_field(name="Timeout duration", value=f"```{self.massping_timeoutduration if self.massping_action == 'timeout' else 'N/A'}```", inline=False)

        await interaction.channel.send(embed=embed)
        
    
    


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Protect(bot))
