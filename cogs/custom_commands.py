import discord
from discord import app_commands
from discord.ext import commands
import json
import logging

logger = logging.getLogger('discord')

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="createcmd")
    async def create_command(
        self,
        interaction: discord.Interaction,
        name: str,
        response: str,
        description: str = "No description provided"
    ):
        try:
            await self.db.create_command(
                interaction.guild_id,
                name,
                response,
                description,
                interaction.user.id
            )
            await interaction.response.send_message(
                f"Command `{name}` created successfully!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Failed to create command: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="listcmds")
    async def list_commands(self, interaction: discord.Interaction):
        commands = await self.db.get_commands(interaction.guild_id)
        
        if not commands:
            await interaction.response.send_message(
                "No custom commands found.",
                ephemeral=True
            )
            return

        embed = discord.Embed(title="Custom Commands")
        for cmd in commands:
            embed.add_field(
                name=cmd['command_name'],
                value=cmd['description'],
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomCommands(bot)) 