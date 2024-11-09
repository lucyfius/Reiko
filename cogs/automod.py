import discord
from discord import app_commands
from discord.ext import commands
import re
import logging
from typing import Optional, List
import aiohttp
import unicodedata
from better_profanity import Profanity
import datetime

logger = logging.getLogger('discord')

class WordFilter:
    def __init__(self):
        self.profanity = Profanity()
        self.profanity.load_censor_words()
        
    def normalize_text(self, text: str) -> str:
        """Normalize text to catch evasion attempts"""
        # Remove accents and convert to lowercase
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode()
        # Remove non-alphanumeric characters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Remove duplicate characters (e.g., 'heeello' -> 'hello')
        text = re.sub(r'(.)\1+', r'\1', text)
        return text.lower()

    def contains_slur(self, text: str) -> bool:
        """Check if text contains any slurs"""
        normalized = self.normalize_text(text)
        return self.profanity.contains_profanity(normalized)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.word_filter = WordFilter()
        self.violation_cache = {}

    @app_commands.command(name="wordfilter")
    @app_commands.default_permissions(manage_guild=True)
    async def word_filter_settings(
        self,
        interaction: discord.Interaction,
        action: str = "warn",  # warn, delete, timeout, kick, ban
        notify_channel: Optional[discord.TextChannel] = None
    ):
        """Configure word filter settings"""
        try:
            settings = {
                'filter_action': action,
                'notify_channel': notify_channel.id if notify_channel else None
            }
            
            await self.db.update_filter_settings(interaction.guild_id, settings)
            await interaction.response.send_message(
                "Word filter settings updated!",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in word_filter_settings: {e}")
            await interaction.response.send_message(
                "Failed to update settings.",
                ephemeral=True
            )

    async def handle_violation(self, message: discord.Message, severity: int):
        """Handle a word filter violation"""
        settings = await self.db.get_filter_settings(message.guild.id)
        action = settings.get('filter_action', 'warn')
        
        # Delete message
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass

        # Get or create violation count
        guild_violations = self.violation_cache.setdefault(message.guild.id, {})
        user_violations = guild_violations.setdefault(message.author.id, 0) + 1
        guild_violations[message.author.id] = user_violations

        # Take action based on number of violations
        if action == 'timeout' and user_violations >= 3:
            try:
                duration = discord.utils.utcnow() + datetime.timedelta(minutes=30)
                await message.author.timeout(duration, reason="AutoMod: Repeated hate speech violations")
            except discord.Forbidden:
                logger.warning(f"Cannot timeout user {message.author.id}")
        
        elif action == 'kick' and user_violations >= 3:
            try:
                await message.author.kick(reason="AutoMod: Repeated hate speech violations")
            except discord.Forbidden:
                logger.warning(f"Cannot kick user {message.author.id}")
        
        elif action == 'ban' and user_violations >= 3:
            try:
                await message.author.ban(reason="AutoMod: Repeated hate speech violations")
            except discord.Forbidden:
                logger.warning(f"Cannot ban user {message.author.id}")

        # Log violation
        await self.log_violation(message, severity)

    async def log_violation(self, message: discord.Message, severity: int):
        """Log a word filter violation"""
        settings = await self.db.get_filter_settings(message.guild.id)
        notify_channel = settings.get('notify_channel')
        
        if notify_channel:
            channel = message.guild.get_channel(notify_channel)
            if channel:
                embed = discord.Embed(
                    title="AutoMod: Hate Speech Detection",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(
                    name="User",
                    value=f"{message.author} ({message.author.id})"
                )
                embed.add_field(
                    name="Channel",
                    value=message.channel.mention
                )
                embed.add_field(
                    name="Severity",
                    value=f"Level {severity}"
                )
                await channel.send(embed=embed)

        # Log to database
        await self.db.log_filter_violation(
            guild_id=message.guild.id,
            user_id=message.author.id,
            channel_id=message.channel.id,
            severity=severity
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Check for filter bypass attempts
        if self.word_filter.contains_slur(message.content):
            await self.handle_violation(message, severity=3)
            return

async def setup(bot):
    await bot.add_cog(AutoMod(bot))