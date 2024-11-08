from dotenv import load_dotenv
import os
import pathlib

# Print current working directory
print(f"Current directory: {pathlib.Path.cwd()}")

# Print .env file existence
env_path = pathlib.Path('.env')
print(f".env file exists: {env_path.exists()}")

# Try to load .env
load_dotenv()

# Check token
token = os.getenv('DISCORD_TOKEN')
print(f"Token found: {'Yes' if token else 'No'}")
if token:
    print(f"Token starts with: {token[:10]}...") 