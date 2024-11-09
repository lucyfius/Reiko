import discord
from discord import app_commands
from discord.ext import commands
import logging
import re
import aiohttp
from typing import Optional
from io import BytesIO

logger = logging.getLogger('discord')

class EmojiTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Regex patterns for different emoji types
        self.custom_emoji_pattern = re.compile(r'<(a)?:([a-zA-Z0-9_]+):(\d+)>')
        self.unicode_emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]')

    @app_commands.command(name="steal", description="Steal an emoji and add it to this server")
    @app_commands.default_permissions(manage_emojis=True)
    async def steal_emoji(
        self,
        interaction: discord.Interaction,
        emoji: str,
        name: Optional[str] = None
    ):
        """Steal an emoji and add it to the server"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if the server has space for new emojis
            guild = interaction.guild
            if len(guild.emojis) >= guild.emoji_limit:
                await interaction.followup.send(
                    "This server has reached its emoji limit!",
                    ephemeral=True
                )
                return

            # Extract emoji information
            emoji_url = None
            emoji_name = name

            # Check if it's a custom emoji
            custom_match = self.custom_emoji_pattern.match(emoji)
            if custom_match:
                is_animated = bool(custom_match.group(1))
                emoji_name = emoji_name or custom_match.group(2)
                emoji_id = custom_match.group(3)
                extension = 'gif' if is_animated else 'png'
                emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}.{extension}'
            
            # If no URL found, emoji might be invalid
            if not emoji_url:
                await interaction.followup.send(
                    "Please provide a valid custom emoji!",
                    ephemeral=True
                )
                return

            # Download emoji
            async with aiohttp.ClientSession() as session:
                async with session.get(emoji_url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(
                            "Failed to download emoji!",
                            ephemeral=True
                        )
                        return
                    emoji_bytes = await resp.read()

            # Create emoji in server
            try:
                new_emoji = await guild.create_custom_emoji(
                    name=emoji_name,
                    image=emoji_bytes,
                    reason=f"Emoji stolen by {interaction.user}"
                )
                
                embed = discord.Embed(
                    title="Emoji Stolen!",
                    description=f"Successfully added {new_emoji} as :{new_emoji.name}:",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=emoji_url)
                embed.add_field(
                    name="Added by",
                    value=interaction.user.mention
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
            except discord.Forbidden:
                await interaction.followup.send(
                    "I don't have permission to add emojis!",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.followup.send(
                    f"Failed to add emoji: {str(e)}",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error in steal_emoji: {e}")
            await interaction.followup.send(
                "An error occurred while stealing the emoji.",
                ephemeral=True
            )

    @app_commands.command(name="enlarge", description="Get an enlarged version of an emoji")
    async def enlarge_emoji(
        self,
        interaction: discord.Interaction,
        emoji: str
    ):
        """Get an enlarged version of an emoji"""
        try:
            # Check if it's a custom emoji
            custom_match = self.custom_emoji_pattern.match(emoji)
            if custom_match:
                is_animated = bool(custom_match.group(1))
                emoji_id = custom_match.group(3)
                extension = 'gif' if is_animated else 'png'
                emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}.{extension}'
                
                embed = discord.Embed(title="Enlarged Emoji")
                embed.set_image(url=emoji_url)
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "Please provide a valid custom emoji!",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error in enlarge_emoji: {e}")
            await interaction.response.send_message(
                "An error occurred while enlarging the emoji.",
                ephemeral=True
            )

    @app_commands.command(name="emojiinfo", description="Get information about an emoji")
    async def emoji_info(
        self,
        interaction: discord.Interaction,
        emoji: str
    ):
        """Get detailed information about an emoji"""
        try:
            # Check if it's a custom emoji
            custom_match = self.custom_emoji_pattern.match(emoji)
            if custom_match:
                is_animated = bool(custom_match.group(1))
                emoji_name = custom_match.group(2)
                emoji_id = custom_match.group(3)
                extension = 'gif' if is_animated else 'png'
                emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}.{extension}'
                
                embed = discord.Embed(
                    title="Emoji Information",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Name", value=f":{emoji_name}:")
                embed.add_field(name="ID", value=emoji_id)
                embed.add_field(name="Animated", value="Yes" if is_animated else "No")
                embed.add_field(
                    name="Direct URL",
                    value=f"[Click here]({emoji_url})"
                )
                embed.set_thumbnail(url=emoji_url)
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "Please provide a valid custom emoji!",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error in emoji_info: {e}")
            await interaction.response.send_message(
                "An error occurred while getting emoji information.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(EmojiTools(bot))
