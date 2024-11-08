import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('discord')

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Basic cog initialized")

    @app_commands.command(name="ping", description="Check bot's latency")
    async def ping(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(
                f"Pong! 🏓 Latency: {round(self.bot.latency * 1000)}ms",
                ephemeral=True
            )
            logger.info(f"Ping command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("An error occurred.", ephemeral=True)

    @app_commands.command(name="info", description="Get information about the bot")
    async def info(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title="Reiko Bot Info",
                description="A Discord bot for advanced administration & fun!",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Commands", 
                value=f"Total Commands: {len(self.bot.tree.get_commands())}"
            )
            embed.add_field(
                name="Servers", 
                value=f"Serving {len(self.bot.guilds)} servers"
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"Info command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("An error occurred.", ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logger.error(f"Command error in Basic cog: {error}")

async def setup(bot):
    await bot.add_cog(Basic(bot)) 