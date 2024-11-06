import discord
from discord import app_commands
from discord.ext import commands
import json
import logging

logger = logging.getLogger('discord')

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = {}
        self.load_reaction_roles()

    def load_reaction_roles(self):
        try:
            with open('data/reaction_roles.json', 'r') as f:
                self.reaction_roles = json.load(f)
        except FileNotFoundError:
            self.reaction_roles = {}

    def save_reaction_roles(self):
        with open('data/reaction_roles.json', 'w') as f:
            json.dump(self.reaction_roles, f, indent=4)

    @app_commands.command(name="createreactionrole", description="Create a reaction role message")
    @app_commands.default_permissions(manage_roles=True)
    async def create_reaction_role(
        self, 
        interaction: discord.Interaction, 
        title: str, 
        description: str,
        channel: discord.TextChannel
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        
        message = await channel.send(embed=embed)
        
        # Store message ID for future reference
        self.reaction_roles[str(message.id)] = {
            "roles": {},
            "channel_id": channel.id
        }
        self.save_reaction_roles()
        
        await interaction.response.send_message("Reaction role message created! Use /addrole to add roles.", ephemeral=True)

    @app_commands.command(name="addrole", description="Add a role to a reaction role message")
    @app_commands.default_permissions(manage_roles=True)
    async def add_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        role: discord.Role,
        emoji: str
    ):
        if message_id not in self.reaction_roles:
            await interaction.response.send_message("Invalid message ID!", ephemeral=True)
            return

        self.reaction_roles[message_id]["roles"][emoji] = role.id
        self.save_reaction_roles()

        # Get the message and add the reaction
        channel = self.bot.get_channel(self.reaction_roles[message_id]["channel_id"])
        message = await channel.fetch_message(int(message_id))
        await message.add_reaction(emoji)

        await interaction.response.send_message(f"Added role {role.name} with emoji {emoji}", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        message_id = str(payload.message_id)
        if message_id in self.reaction_roles:
            emoji = str(payload.emoji)
            if emoji in self.reaction_roles[message_id]["roles"]:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(self.reaction_roles[message_id]["roles"][emoji])
                member = guild.get_member(payload.user_id)
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        message_id = str(payload.message_id)
        if message_id in self.reaction_roles:
            emoji = str(payload.emoji)
            if emoji in self.reaction_roles[message_id]["roles"]:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(self.reaction_roles[message_id]["roles"][emoji])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
