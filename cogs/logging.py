import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger('discord')

class EventLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_settings = {}
        self.load_settings()
        self.audit_logs = {}
        
    def load_settings(self):
        try:
            with open('data/log_settings.json', 'r') as f:
                self.log_settings = json.load(f)
        except FileNotFoundError:
            self.log_settings = {}
            
    def save_settings(self):
        with open('data/log_settings.json', 'w') as f:
            json.dump(self.log_settings, f, indent=4)

    async def log_event(self, guild_id: int, event_type: str, embed: discord.Embed):
        guild_id = str(guild_id)
        if guild_id in self.log_settings and event_type in self.log_settings[guild_id]:
            channel_id = self.log_settings[guild_id][event_type]
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=embed)

    @app_commands.command(name="setlogchannel", description="Set a logging channel for specific events")
    @app_commands.default_permissions(manage_guild=True)
    async def set_log_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        event_type: str = "all"
    ):
        guild_id = str(interaction.guild_id)
        if guild_id not in self.log_settings:
            self.log_settings[guild_id] = {}
            
        self.log_settings[guild_id][event_type] = channel.id
        self.save_settings()
        
        await interaction.response.send_message(
            f"Set {channel.mention} as logging channel for {event_type} events",
            ephemeral=True
        )

    # Event Listeners
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
            
        embed = discord.Embed(
            title="Message Deleted",
            description=f"Message by {message.author.mention} deleted in {message.channel.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Content", value=message.content or "No content", inline=False)
        
        await self.log_event(message.guild.id, "message_delete", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
            
        if before.content == after.content:
            return
            
        embed = discord.Embed(
            title="Message Edited",
            description=f"Message by {before.author.mention} edited in {before.channel.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        
        await self.log_event(before.guild.id, "message_edit", embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="Member Joined",
            description=f"{member.mention} joined the server",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        await self.log_event(member.guild.id, "member_join", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Member Left",
            description=f"{member.mention} left the server",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await self.log_event(member.guild.id, "member_remove", embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                reason = entry.reason or "No reason provided"
                moderator = entry.user
                break
        else:
            reason = "No reason found"
            moderator = None

        embed = discord.Embed(
            title="Member Banned",
            description=f"{user.mention} was banned",
            color=discord.Color.dark_red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        if moderator:
            embed.add_field(name="Banned by", value=moderator.mention)
            
        await self.log_event(guild.id, "member_ban", embed)

async def setup(bot):
    await bot.add_cog(EventLogging(bot)) 