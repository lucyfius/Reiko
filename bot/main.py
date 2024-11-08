import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncpg
import ssl
import logging
import pathlib
import sys

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# Load environment variables at the start
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("No Discord token found in .env file")

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.db = None

    async def setup_hook(self):
        # Create SSL context
        ssl_context = ssl.create_default_context(
            cafile="certs/root.crt"
        )
        
        # Create database pool
        try:
            self.db = await asyncpg.create_pool(
                os.getenv('DATABASE_URL'),
                ssl=ssl_context,
                min_size=5,
                max_size=20
            )
            logger.info("Successfully connected to database!")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

        # Clear existing commands and sync new ones
        logger.info("Clearing and syncing commands...")
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        
        # Load all cogs
        cogs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cogs')
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f"Loaded extension: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load extension {filename}: {e}")

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name}')
        
        # Sync commands again when ready
        try:
            commands = await self.tree.sync()
            logger.info(f"Synced {len(commands)} command(s)")
            for cmd in commands:
                logger.info(f"Registered command: /{cmd.name}")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_interaction(self, interaction: discord.Interaction):
        logger.info(f"Interaction received from {interaction.user}: {interaction.command.name if interaction.command else 'Unknown'}")

    async def on_command_error(self, ctx, error):
        logger.error(f"Command error: {error}")

async def main():
    logger.info(f"Current directory: {pathlib.Path.cwd()}")
    logger.info(f"Token available: {'Yes' if TOKEN else 'No'}")
    
    bot = Bot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())