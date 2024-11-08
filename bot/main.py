import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncpg
import ssl
import logging

logger = logging.getLogger('discord')

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.db = None  # Will store our database pool

    async def setup_hook(self):
        # Load environment variables
        load_dotenv()
        
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

        # Load all cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f"Loaded extension: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load extension {filename}: {e}")

    async def close(self):
        # Cleanup
        if self.db:
            await self.db.close()
        await super().close()

async def main():
    bot = Bot()
    async with bot:
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 