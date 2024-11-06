import discord
from discord.ext import commands
import json
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# Bot configuration
class LumiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        
        super().__init__(
            command_prefix="!",  # Fallback prefix
            intents=intents,
            help_command=None  # We'll implement our own help command
        )
        
        # Store bot configuration
        self.config = {}
        self.load_config()
        
    async def setup_hook(self):
        # Load all cogs
        await self.load_extensions()
        
    def load_config(self):
        try:
            with open('config/config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
            self.save_config()
            
    def save_config(self):
        with open('config/config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
            
    async def load_extensions(self):
        """Load all extensions (cogs) from the cogs directory"""
        for file in Path('cogs').glob('*.py'):
            if file.name != '__init__.py':
                extension = f"cogs.{file.stem}"
                try:
                    await self.load_extension(extension)
                    logger.info(f"Loaded extension {extension}")
                except Exception as e:
                    logger.error(f"Failed to load extension {extension}: {e}")

bot = LumiBot()

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.tree.sync()  # Sync slash commands

def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found in environment variables")
    bot.run(token)

if __name__ == "__main__":
    main() 