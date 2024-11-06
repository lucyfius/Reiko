import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger('discord')

class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduled_announcements = {}
        self.announcement_templates = {}
        self.load_data()
        self.bg_task = self.bot.loop.create_task(self.check_scheduled_announcements())

    def load_data(self):
        try:
            with open('data/announcements.json', 'r') as f:
                data = json.load(f)
                self.scheduled_announcements = data.get('scheduled', {})
                self.announcement_templates = data.get('templates', {})
        except FileNotFoundError:
            self.save_data()

    def save_data(self):
        with open('data/announcements.json', 'w') as f:
            json.dump({
                'scheduled': self.scheduled_announcements,
                'templates': self.announcement_templates
            }, f, indent=4)

    @app_commands.command(name="announce", description="Create an announcement")
    @app_commands.default_permissions(manage_messages=True)
    async def announce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        content: str,
        color: str = "blue",
        ping_role: discord.Role = None
    ):
        try:
            color_value = getattr(discord.Color, color)()
        except AttributeError:
            color_value = discord.Color.blue()

        embed = discord.Embed(
            title=title,
            description=content,
            color=color_value,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text=f"Announced by {interaction.user.display_name}")
        
        content = None
        if ping_role:
            content = ping_role.mention

        await channel.send(content=content, embed=embed)
        await interaction.response.send_message("Announcement sent!", ephemeral=True)

    @app_commands.command(name="schedule", description="Schedule an announcement")
    @app_commands.default_permissions(manage_messages=True)
    async def schedule_announcement(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        content: str,
        time: str,  # Format: YYYY-MM-DD HH:MM
        repeat: str = None  # daily, weekly, monthly, or None
    ):
        try:
            schedule_time = datetime.strptime(time, "%Y-%m-%d %H:%M")
        except ValueError:
            await interaction.response.send_message(
                "Invalid time format! Use YYYY-MM-DD HH:MM",
                ephemeral=True
            )
            return

        announcement_id = str(len(self.scheduled_announcements) + 1)
        self.scheduled_announcements[announcement_id] = {
            'channel_id': channel.id,
            'title': title,
            'content': content,
            'time': time,
            'repeat': repeat,
            'guild_id': interaction.guild_id
        }
        
        self.save_data()
        
        await interaction.response.send_message(
            f"Announcement scheduled for {time}",
            ephemeral=True
        )

    @app_commands.command(name="template", description="Save an announcement template")
    @app_commands.default_permissions(manage_messages=True)
    async def save_template(
        self,
        interaction: discord.Interaction,
        name: str,
        title: str,
        content: str
    ):
        guild_id = str(interaction.guild_id)
        if guild_id not in self.announcement_templates:
            self.announcement_templates[guild_id] = {}
            
        self.announcement_templates[guild_id][name] = {
            'title': title,
            'content': content
        }
        
        self.save_data()
        
        await interaction.response.send_message(
            f"Template '{name}' saved!",
            ephemeral=True
        )

    @app_commands.command(name="usetemplate", description="Use a saved template")
    @app_commands.default_permissions(manage_messages=True)
    async def use_template(
        self,
        interaction: discord.Interaction,
        template_name: str,
        channel: discord.TextChannel
    ):
        guild_id = str(interaction.guild_id)
        if (guild_id not in self.announcement_templates or 
            template_name not in self.announcement_templates[guild_id]):
            await interaction.response.send_message(
                "Template not found!",
                ephemeral=True
            )
            return
            
        template = self.announcement_templates[guild_id][template_name]
        embed = discord.Embed(
            title=template['title'],
            description=template['content'],
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        await channel.send(embed=embed)
        await interaction.response.send_message(
            "Announcement sent using template!",
            ephemeral=True
        )

    async def check_scheduled_announcements(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            current_time = datetime.utcnow()
            to_remove = []
            
            for announcement_id, data in self.scheduled_announcements.items():
                schedule_time = datetime.strptime(data['time'], "%Y-%m-%d %H:%M")
                
                if current_time >= schedule_time:
                    channel = self.bot.get_channel(data['channel_id'])
                    if channel:
                        embed = discord.Embed(
                            title=data['title'],
                            description=data['content'],
                            color=discord.Color.blue(),
                            timestamp=current_time
                        )
                        await channel.send(embed=embed)
                    
                    if data['repeat']:
                        # Update next schedule time based on repeat type
                        if data['repeat'] == 'daily':
                            next_time = schedule_time + timedelta(days=1)
                        elif data['repeat'] == 'weekly':
                            next_time = schedule_time + timedelta(weeks=1)
                        elif data['repeat'] == 'monthly':
                            next_time = schedule_time + timedelta(days=30)
                            
                        data['time'] = next_time.strftime("%Y-%m-%d %H:%M")
                    else:
                        to_remove.append(announcement_id)
            
            for announcement_id in to_remove:
                del self.scheduled_announcements[announcement_id]
                
            self.save_data()
            await asyncio.sleep(60)  # Check every minute

async def setup(bot):
    await bot.add_cog(Announcements(bot)) 