import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger('discord')

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        logger.info("Welcome cog initialized")

    @app_commands.command(name="setwelcome", description="Set welcome message settings")
    @app_commands.default_permissions(manage_guild=True)
    async def set_welcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
        dm_message: Optional[str] = None,
        embed: bool = True
    ):
        try:
            await self.db.set_welcome(
                interaction.guild_id,
                channel.id,
                message,
                dm_message,
                embed
            )
            await interaction.response.send_message(
                "Welcome message settings updated!",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error setting welcome message: {e}")
            await interaction.response.send_message(
                "Failed to update welcome settings.",
                ephemeral=True
            )

    @app_commands.command(name="testwelcome", description="Test welcome message")
    @app_commands.default_permissions(manage_guild=True)
    async def test_welcome(self, interaction: discord.Interaction):
        await self.send_welcome_message(interaction.member)
        await interaction.response.send_message(
            "Test welcome message sent!",
            ephemeral=True
        )

    async def send_welcome_message(self, member):
        try:
            settings = await self.db.get_welcome_settings(member.guild.id)
            if not settings:
                return

            channel = member.guild.get_channel(settings['channel_id'])
            if not channel:
                return

            message = settings['welcome_message']
            message = message.replace('{user}', member.mention)
            message = message.replace('{server}', member.guild.name)
            message = message.replace('{count}', str(member.guild.member_count))

            if settings['use_embed']:
                embed = discord.Embed(
                    title=f"Welcome to {member.guild.name}!",
                    description=message,
                    color=discord.Color.blue()
                )
                await channel.send(embed=embed)
            else:
                await channel.send(message)

            if settings['dm_message']:
                try:
                    dm_msg = settings['dm_message'].replace('{server}', member.guild.name)
                    await member.send(dm_msg)
                except discord.Forbidden:
                    logger.warning(f"Could not send DM to {member}")
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send_welcome_message(member)

async def setup(bot):
    await bot.add_cog(Welcome(bot)) 