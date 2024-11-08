import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('discord')

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="createreactionrole")
    async def create_reaction_role(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role,
        emoji: str,
        description: str
    ):
        # Create message
        message = await channel.send(f"React with {emoji} to get the {role.mention} role\n{description}")
        await message.add_reaction(emoji)

        # Store in database
        await self.db.add_reaction_role(
            interaction.guild_id,
            message.id,
            channel.id,
            role.id,
            emoji
        )

        await interaction.response.send_message("Reaction role created!", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        # Get reaction role from database
        reaction_roles = await self.db.get_reaction_roles(payload.guild_id)
        
        for rr in reaction_roles:
            if (rr['message_id'] == payload.message_id and 
                rr['emoji'] == str(payload.emoji)):
                role = payload.member.guild.get_role(rr['role_id'])
                if role:
                    await payload.member.add_roles(role)
                break

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
