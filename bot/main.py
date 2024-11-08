import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncpg
import ssl
import logging
import sys
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger('discord')

# Load environment variables
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
        logger.info("Bot initialized")

    async def setup_hook(self):
        logger.info("Setting up bot...")
        
        # Database setup
        try:
            ssl_context = ssl.create_default_context(
                cafile="certs/root.crt"
            )
            self.db = await asyncpg.create_pool(
                os.getenv('DATABASE_URL'),
                ssl=ssl_context,
                min_size=5,
                max_size=20
            )
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            logger.error(traceback.format_exc())
            raise

        # Clear existing commands
        logger.info("Clearing existing commands...")
        self.tree.clear_commands(guild=None)
        await self.tree.sync()

        # Load cogs
        try:
            cogs_dir = Path(__file__).parent.parent / 'cogs'
            for filename in os.listdir(cogs_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        logger.info(f"Loaded cog: {filename}")
                    except Exception as e:
                        logger.error(f"Failed to load {filename}: {e}")
                        logger.error(traceback.format_exc())
        except Exception as e:
            logger.error(f"Error loading cogs: {e}")
            logger.error(traceback.format_exc())

        # Sync commands
        try:
            commands = await self.tree.sync()
            logger.info(f"Synced {len(commands)} commands")
            for cmd in commands:
                logger.info(f"Registered: /{cmd.name}")
        except Exception as e:
            logger.error(f"Command sync failed: {e}")
            logger.error(traceback.format_exc())

    async def on_ready(self):
        logger.info(f"Bot is ready: {self.user.name} ({self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

    async def on_command_error(self, ctx, error):
        logger.error(f"Command error: {error}")
        logger.error(traceback.format_exc())

async def main():
    try:
        async with Bot() as bot:
            logger.info("Starting bot...")
            await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())