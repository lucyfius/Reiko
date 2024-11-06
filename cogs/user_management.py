import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger('discord')

class UserManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.raid_protection = {}
        self.user_stats = {}
        self.load_stats()
        
    def load_stats(self):
        try:
            with open('data/user_stats.json', 'r') as f:
                self.user_stats = json.load(f)
        except FileNotFoundError:
            self.user_stats = {}
            
    def save_stats(self):
        with open('data/user_stats.json', 'w') as f:
            json.dump(self.user_stats, f, indent=4)

    @app_commands.command(name="tempban", description="Temporarily ban a user")
    @app_commands.default_permissions(ban_members=True)
    async def temp_ban(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: int,
        reason: str = None
    ):
        """Duration in minutes"""
        await user.ban(reason=f"Temporary ban: {reason}")
        
        # Schedule unban
        await interaction.response.send_message(
            f"{user.mention} has been banned for {duration} minutes.\nReason: {reason}",
            ephemeral=True
        )
        
        await asyncio.sleep(duration * 60)
        await interaction.guild.unban(user, reason="Temporary ban expired")

    @app_commands.command(name="tempmute", description="Temporarily mute a user")
    @app_commands.default_permissions(moderate_members=True)
    async def temp_mute(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: int,
        reason: str = None
    ):
        """Duration in minutes"""
        await user.timeout(
            duration=timedelta(minutes=duration),
            reason=reason
        )
        
        await interaction.response.send_message(
            f"{user.mention} has been muted for {duration} minutes.\nReason: {reason}",
            ephemeral=True
        )

    @app_commands.command(name="userinfo", description="Get information about a user")
    async def user_info(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(user.id)
        
        if guild_id not in self.user_stats:
            self.user_stats[guild_id] = {}
        if user_id not in self.user_stats[guild_id]:
            self.user_stats[guild_id][user_id] = {
                "message_count": 0,
                "last_active": None,
                "join_date": user.joined_at.isoformat() if user.joined_at else None
            }
            
        stats = self.user_stats[guild_id][user_id]
        
        embed = discord.Embed(
            title=f"User Information - {user.display_name}",
            color=user.color,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Message Count", value=stats["message_count"])
        embed.add_field(name="Roles", value=" ".join([role.mention for role in user.roles[1:]]) or "No roles")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="raidmode", description="Toggle raid protection mode")
    @app_commands.default_permissions(administrator=True)
    async def raid_mode(
        self,
        interaction: discord.Interaction,
        enabled: bool
    ):
        guild_id = str(interaction.guild_id)
        self.raid_protection[guild_id] = enabled
        
        await interaction.response.send_message(
            f"Raid protection mode {'enabled' if enabled else 'disabled'}",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        
        # Check raid protection
        if guild_id in self.raid_protection and self.raid_protection[guild_id]:
            account_age = datetime.utcnow() - member.created_at
            if account_age.days < 7:  # Account less than 7 days old
                await member.kick(reason="Raid protection: Account too new")
                return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        if guild_id not in self.user_stats:
            self.user_stats[guild_id] = {}
        if user_id not in self.user_stats[guild_id]:
            self.user_stats[guild_id][user_id] = {
                "message_count": 0,
                "last_active": None,
                "join_date": message.author.joined_at.isoformat() if message.author.joined_at else None
            }
            
        self.user_stats[guild_id][user_id]["message_count"] += 1
        self.user_stats[guild_id][user_id]["last_active"] = datetime.utcnow().isoformat()
        self.save_stats()

async def setup(bot):
    await bot.add_cog(UserManagement(bot)) 