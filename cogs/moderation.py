import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('discord')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Database manager instance

    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        try:
            warning_count = await self.db.add_warning(
                interaction.guild_id,
                user.id,
                interaction.user.id,
                reason
            )

            # Handle automated actions based on warning count
            action_taken = "warned"
            if warning_count == 3:
                await user.timeout(duration=3600)
                action_taken = "timed out for 1 hour"
            elif warning_count == 5:
                await user.kick(reason=f"Received {warning_count} warnings")
                action_taken = "kicked"
            elif warning_count >= 7:
                await user.ban(reason=f"Received {warning_count} warnings")
                action_taken = "banned"

            await interaction.response.send_message(
                f"{user.mention} has been {action_taken}. "
                f"This is warning #{warning_count}.\nReason: {reason}",
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"Error in warn command: {e}")
            await interaction.response.send_message(
                "An error occurred while processing the warning.",
                ephemeral=True
            )

    @app_commands.command(name="warnings", description="View warnings for a user")
    @app_commands.default_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        try:
            warnings = await self.db.get_warnings(interaction.guild_id, user.id)
            
            if not warnings:
                await interaction.response.send_message(
                    f"{user.mention} has no warnings.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title=f"Warnings for {user.display_name}",
                color=discord.Color.yellow()
            )

            for warning in warnings:
                moderator = interaction.guild.get_member(warning['moderator_id'])
                mod_name = moderator.display_name if moderator else "Unknown Moderator"
                
                embed.add_field(
                    name=f"Warning at {warning['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                    value=f"Reason: {warning['reason']}\nModerator: {mod_name}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in warnings command: {e}")
            await interaction.response.send_message(
                "An error occurred while fetching warnings.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Moderation(bot)) 