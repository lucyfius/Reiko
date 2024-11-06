import discord
from discord import app_commands
from discord.ext import commands
import json
import logging

logger = logging.getLogger('discord')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warning_counts = {}
        self.load_warnings()
        
    def load_warnings(self):
        try:
            with open('data/warnings.json', 'r') as f:
                self.warning_counts = json.load(f)
        except FileNotFoundError:
            self.warning_counts = {}
            
    def save_warnings(self):
        with open('data/warnings.json', 'w') as f:
            json.dump(self.warning_counts, f, indent=4)
            
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        # Convert user ID to string for JSON storage
        user_id = str(user.id)
        
        if user_id not in self.warning_counts:
            self.warning_counts[user_id] = []
            
        self.warning_counts[user_id].append({
            "reason": reason,
            "moderator": interaction.user.id,
            "timestamp": discord.utils.utcnow().isoformat()
        })
        
        self.save_warnings()
        
        warning_count = len(self.warning_counts[user_id])
        
        # Handle automated actions based on warning count
        action_taken = "warned"
        if warning_count == 3:
            await user.timeout(duration=3600)  # 1 hour timeout
            action_taken = "timed out for 1 hour"
        elif warning_count == 5:
            await user.kick(reason=f"Received {warning_count} warnings")
            action_taken = "kicked"
        elif warning_count >= 7:
            await user.ban(reason=f"Received {warning_count} warnings")
            action_taken = "banned"
            
        await interaction.response.send_message(
            f"{user.mention} has been {action_taken}. "
            f"This is warning #{warning_count}.\nReason: {reason}"
        )

async def setup(bot):
    await bot.add_cog(Moderation(bot)) 