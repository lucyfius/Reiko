import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
import logging
from utils.word_filter import EnhancedWordFilter
import io
import csv

logger = logging.getLogger('discord')

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.word_filter = EnhancedWordFilter(self.db)

    @app_commands.command(name="addpattern")
    @app_commands.default_permissions(manage_guild=True)
    async def add_pattern(
        self,
        interaction: discord.Interaction,
        pattern: str,
        category: str,
        severity: int = 1,
        is_regex: bool = False,
        description: str = None
    ):
        """Add a new filter pattern"""
        try:
            await self.db.add_filter_pattern(
                guild_id=interaction.guild_id,
                pattern=pattern,
                regex_pattern=pattern if is_regex else None,
                severity=severity,
                category=category,
                description=description,
                is_regex=is_regex,
                created_by=interaction.user.id
            )
            
            # Refresh patterns
            await self.word_filter.load_patterns(interaction.guild_id)
            
            await interaction.response.send_message(
                f"Added new pattern to category '{category}'",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error adding pattern: {e}")
            await interaction.response.send_message(
                "Failed to add pattern.",
                ephemeral=True
            )

    @app_commands.command(name="importpatterns")
    @app_commands.default_permissions(manage_guild=True)
    async def import_patterns(
        self,
        interaction: discord.Interaction,
        file: discord.Attachment
    ):
        """Import patterns from CSV file"""
        if not file.filename.endswith('.csv'):
            await interaction.response.send_message(
                "Please provide a CSV file.",
                ephemeral=True
            )
            return

        try:
            content = await file.read()
            csv_content = content.decode('utf-8').splitlines()
            reader = csv.DictReader(csv_content)
            
            patterns_added = 0
            for row in reader:
                await self.db.add_filter_pattern(
                    guild_id=interaction.guild_id,
                    pattern=row['pattern'],
                    regex_pattern=row.get('regex_pattern'),
                    severity=int(row.get('severity', 1)),
                    category=row.get('category', 'default'),
                    description=row.get('description'),
                    is_regex=row.get('is_regex', '').lower() == 'true',
                    created_by=interaction.user.id
                )
                patterns_added += 1

            await self.word_filter.load_patterns(interaction.guild_id)
            
            await interaction.response.send_message(
                f"Successfully imported {patterns_added} patterns.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error importing patterns: {e}")
            await interaction.response.send_message(
                "Failed to import patterns.",
                ephemeral=True
            )

    @app_commands.command(name="exportpatterns")
    @app_commands.default_permissions(manage_guild=True)
    async def export_patterns(self, interaction: discord.Interaction):
        """Export all patterns to CSV"""
        try:
            patterns = await self.db.get_filter_patterns(interaction.guild_id)
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'pattern', 'regex_pattern', 'severity', 'category',
                'description', 'is_regex'
            ])
            
            writer.writeheader()
            for pattern in patterns:
                writer.writerow({
                    'pattern': pattern['pattern'],
                    'regex_pattern': pattern['regex_pattern'],
                    'severity': pattern['severity'],
                    'category': pattern['category'],
                    'description': pattern['description'],
                    'is_regex': pattern['is_regex']
                })
            
            file = discord.File(
                io.StringIO(output.getvalue()),
                filename='filter_patterns.csv'
            )
            await interaction.response.send_message(
                "Here are your filter patterns:",
                file=file,
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error exporting patterns: {e}")
            await interaction.response.send_message(
                "Failed to export patterns.",
                ephemeral=True
            )

    @app_commands.command(name="violations")
    @app_commands.default_permissions(manage_guild=True)
    async def view_violations(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None,
        category: Optional[str] = None
    ):
        """View filter violations"""
        try:
            violations = await self.db.get_filter_violations(
                guild_id=interaction.guild_id,
                user_id=user.id if user else None,
                category=category
            )
            
            if not violations:
                await interaction.response.send_message(
                    "No violations found.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="Filter Violations",
                color=discord.Color.red()
            )
            
            for v in violations[:10]:  # Show last 10 violations
                embed.add_field(
                    name=f"Violation by {self.bot.get_user(v['user_id'])}",
                    value=f"Category: {v['category']}\n"
                          f"Severity: {v['severity']}\n"
                          f"Action: {v['action_taken']}\n"
                          f"Time: {v['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error viewing violations: {e}")
            await interaction.response.send_message(
                "Failed to retrieve violations.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AutoMod(bot))