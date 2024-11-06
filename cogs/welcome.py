import discord
from discord import app_commands
from discord.ext import commands
import json
import logging

logger = logging.getLogger('discord')

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_settings = {}
        self.load_settings()

    def load_settings(self):
        try:
            with open('data/welcome_settings.json', 'r') as f:
                self.welcome_settings = json.load(f)
        except FileNotFoundError:
            self.welcome_settings = {}

    def save_settings(self):
        with open('data/welcome_settings.json', 'w') as f:
            json.dump(self.welcome_settings, f, indent=4)

    @app_commands.command(name="setwelcome", description="Set welcome message settings")
    @app_commands.default_permissions(manage_guild=True)
    async def set_welcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
        dm_message: str = None,
        embed: bool = True
    ):
        guild_id = str(interaction.guild_id)
        self.welcome_settings[guild_id] = {
            'channel_id': channel.id,
            'message': message,
            'dm_message': dm_message,
            'use_embed': embed
        }
        
        self.save_settings()
        
        await interaction.response.send_message(
            "Welcome message settings updated!",
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
        guild_id = str(member.guild.id)
        if guild_id not in self.welcome_settings:
            return

        settings = self.welcome_settings[guild_id]
        channel = member.guild.get_channel(settings['channel_id'])
        
        if not channel:
            return

        # Replace placeholders in message
        message = settings['message'].replace('{user}', member.mention)
        message = message.replace('{server}', member.guild.name)
        message = message.replace('{count}', str(member.guild.member_count))

        if settings.get('use_embed', True):
            embed = discord.Embed(
                title=f"Welcome to {member.guild.name}!",
                description=message,
                color=discord.Color.blue()
            )
            await channel.send(embed=embed)
        else:
            await channel.send(message)

async def setup(bot):
    await bot.add_cog(Welcome(bot)) 