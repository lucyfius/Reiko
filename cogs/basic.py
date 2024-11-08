import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('discord')

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check if the bot is alive")
    async def ping(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Pong! 🏓 ({round(self.bot.latency * 1000)}ms)")
            logger.info(f"Ping command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("An error occurred.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Basic(bot)) 