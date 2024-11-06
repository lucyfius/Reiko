import discord
from discord import app_commands
from discord.ext import commands
import json
import logging

logger = logging.getLogger('discord')

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.custom_commands = {}
        self.load_commands()

    def load_commands(self):
        try:
            with open('data/custom_commands.json', 'r') as f:
                self.custom_commands = json.load(f)
        except FileNotFoundError:
            self.custom_commands = {}

    def save_commands(self):
        with open('data/custom_commands.json', 'w') as f:
            json.dump(self.custom_commands, f, indent=4)

    @app_commands.command(name="createcmd", description="Create a custom command")
    @app_commands.default_permissions(manage_guild=True)
    async def create_command(
        self,
        interaction: discord.Interaction,
        command_name: str,
        response: str,
        description: str = "A custom command"
    ):
        guild_id = str(interaction.guild_id)
        
        if guild_id not in self.custom_commands:
            self.custom_commands[guild_id] = {}
            
        self.custom_commands[guild_id][command_name] = {
            "response": response,
            "description": description
        }
        
        self.save_commands()
        
        # Create the command for this guild
        @app_commands.command(name=command_name, description=description)
        async def custom_command(interaction: discord.Interaction):
            await interaction.response.send_message(response)

        self.bot.tree.add_command(custom_command, guild=interaction.guild)
        await self.bot.tree.sync(guild=interaction.guild)
        
        await interaction.response.send_message(f"Created command /{command_name}", ephemeral=True)

    @app_commands.command(name="deletecmd", description="Delete a custom command")
    @app_commands.default_permissions(manage_guild=True)
    async def delete_command(
        self,
        interaction: discord.Interaction,
        command_name: str
    ):
        guild_id = str(interaction.guild_id)
        
        if guild_id in self.custom_commands and command_name in self.custom_commands[guild_id]:
            del self.custom_commands[guild_id][command_name]
            self.save_commands()
            
            # Remove the command
            self.bot.tree.remove_command(command_name, guild=interaction.guild)
            await self.bot.tree.sync(guild=interaction.guild)
            
            await interaction.response.send_message(f"Deleted command /{command_name}", ephemeral=True)
        else:
            await interaction.response.send_message("Command not found!", ephemeral=True)

    @app_commands.command(name="listcmds", description="List all custom commands")
    async def list_commands(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id)
        
        if guild_id not in self.custom_commands or not self.custom_commands[guild_id]:
            await interaction.response.send_message("No custom commands found!", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="Custom Commands",
            color=discord.Color.blue()
        )
        
        for cmd_name, cmd_data in self.custom_commands[guild_id].items():
            embed.add_field(
                name=f"/{cmd_name}",
                value=cmd_data["description"],
                inline=False
            )
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomCommands(bot)) 