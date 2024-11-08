import asyncio
import asyncpg
import os
from dotenv import load_dotenv
import ssl

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    print("Attempting to connect to database...")
    try:
        # Create SSL context with the root certificate
        ssl_context = ssl.create_default_context(
            cafile="certs/root.crt"
        )
        
        # Connect with SSL context
        conn = await asyncpg.connect(
            database_url,
            ssl=ssl_context
        )
        
        # Simple test query
        version = await conn.fetchval('SELECT version()')
        print(f"Successfully connected to database!")
        print(f"Database version: {version}")
        
        # Close the connection
        await conn.close()
        print("Connection closed successfully")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_connection()) 