import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('discord')

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Test if slash commands are working")
    async def test(self, interaction: discord.Interaction):
        try:
            # Defer the response first
            await interaction.response.defer(ephemeral=True)
            
            # Send the actual response
            await interaction.followup.send("Slash commands are working! 🎉")
            logger.info(f"Test command used by {interaction.user} in {interaction.guild.name}")
            
        except Exception as e:
            logger.error(f"Error in test command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "An error occurred while processing the command.",
                    ephemeral=True
                )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        logger.info(f"Interaction received: {interaction.command.name if interaction.command else 'Unknown'}")

async def setup(bot):
    await bot.add_cog(Test(bot)) 