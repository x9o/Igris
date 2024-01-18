import discord, aiohttp, typing, datetime as dt
from discord.ext import commands
from discord import app_commands
from utils.utils import Time, Info

class Loggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook: str = None # 
        self.generateinvitelinks: bool = False #
        
        self.edit_logger: bool = False # 

          
        self.generated_invitelinks: dict = {}
        self.edit_history: dict = {}
    
    
    @app_commands.command(description="Setup logger")
    @app_commands.describe(webhook="Webhook URL",  generate_invite_links="Generate invite links", edit_logger_toggle="Edit logger toggle")
    async def logger_config(self, interaction: discord.Interaction, webhook: str = None, generate_invite_links: bool = False, edit_logger_toggle: bool = True):
        if Info.is_valid_discord_webhook(webhook):
            self.edit_logger = edit_logger_toggle
            self.webhook = webhook
            self.generateinvitelinks = generate_invite_links
            

            embed = discord.Embed(title="<:settingssliders:1196698681869615196> Logger Config", description="", color=discord.Color.green())
            embed.add_field(name="Webhook", value=f"{webhook}", inline=False)
            embed.add_field(name="Generate Invite Links", value=f"```{generate_invite_links}```", inline=False)
            embed.add_field(name="Status", value=f"```{edit_logger_toggle}```", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(title="❌ Error", description="Invalid webhook URL.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=False)

    @commands.command()
    async def history(self, ctx, message_id=None):
        if message_id is None and ctx.message.reference is None:
            v = discord.Embed(title="❌ Please provide a message ID or reply to the target message.", color=discord.Color.red())
            await ctx.send(embed=v)
            return

        if ctx.message.reference is not None:
            message_id = ctx.message.reference.message_id
        else:
            message_id = int(message_id)

        if message_id not in self.edit_history:
            v = discord.Embed(title="❌ Message hasn't been edited/Message edited before bot presence/Message not found.", color=discord.Color.red())
            await ctx.send(embed=v)
            return

        history_data = self.edit_history[message_id]
        original_content = history_data['original_content']
        edits = history_data['edits']

        embed = discord.Embed(title=f"<:document:1196696248992940032> {message_id}", color=discord.Color.dark_purple())
        embed.add_field(name="<:pencil:1196696945478078484> Original Content", value=f"{original_content}", inline=False)

        channel = ctx.channel

        for i, edit in enumerate(edits, start=1):
            content = edit['content']
            date_edited = edit['date_edited']

            embed.add_field(name=f"<:pencil:1196696945478078484> Edit {i}", value=f"{content}", inline=False)
            embed.add_field(name=f"<:calendar:1196697215918424136> Edit {i}: Date", value=Time.timestamp_generate(date_edited), inline=False)

        await ctx.reply(embed=embed)
       


    @commands.Cog.listener()   
    async def on_message_edit(self, before, after):
        message_id = after.id

        if message_id not in self.edit_history:
            self.edit_history[message_id] = {
                'original_content': before.content,
                'edits': []
            }

        self.edit_history[message_id]['edits'].append({
            'content': after.content,
            'date_edited': dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        if self.edit_logger:
            if self.webhook is not None:
            
                embed = discord.Embed(title="<:document:1196696248992940032> Message edited", description=f"{after.id}", color=discord.Color.dark_purple())
                embed.add_field(name="<:angledoubleleft:1196697893525008454> Before: ", value=f"{before.content}", inline=False)
                embed.add_field(name="<:angledoubleright:1196697949804183682> After: ", value=f"**{after.content}**", inline=False)
                embed.add_field(name="<:books:1196698530572668959> Channel: ", value=f"{after.channel.mention}", inline=False)
                embed.add_field(name="<:home:1196698991610560592> Guild: ", value=f"{after.guild}", inline=False)
                embed.add_field(name="<:calendar:1196697215918424136> Date", value=f"{Time.timestamp_generate(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}", inline=False)
                embed.add_field(name="<:pencil:1196696945478078484> Author: ", value=f"{after.author.mention}", inline=False)
                embed.set_thumbnail(url=after.author.avatar.url)
                embed.set_footer(text="Messages sent before bot presence can not be detected when edited.")
                
                
                if self.generateinvitelinks:
                    server_id = str(after.guild.id)
                    if server_id in self.generated_invitelinks:
                        invite_link = self.generated_invitelinks[server_id]
                    else:
                        invite_link = await after.channel.create_invite(max_age=86400, max_uses=1)
                        self.generated_invitelinks[server_id] = invite_link

                    embed.add_field(name=f'🔗 Invite Link: {after.guild}', value=invite_link, inline=False)

                payload = {
                    'embeds': [embed.to_dict()]
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(self.webhook, json=payload):
                        pass

async def setup(bot):
    await bot.add_cog(Loggers(bot))

