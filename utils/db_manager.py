import asyncpg
import logging
from typing import Optional, Dict, List, Any
import os
from dotenv import load_dotenv

logger = logging.getLogger('discord')

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.pool = None
        self.dsn = os.getenv('DATABASE_URL')  # CockroachDB connection string

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=5,
                max_size=20
            )
            await self.init_tables()
            logger.info("Successfully connected to CockroachDB")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def init_tables(self):
        """Initialize database tables"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    guild_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    moderator_id BIGINT NOT NULL,
                    reason TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    INDEX (guild_id, user_id)
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    message_count INT DEFAULT 0,
                    event_type TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    INDEX (guild_id, channel_id)
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS welcome_settings (
                    guild_id BIGINT PRIMARY KEY,
                    channel_id BIGINT NOT NULL,
                    welcome_message TEXT,
                    dm_message TEXT,
                    use_embed BOOLEAN DEFAULT true
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS custom_commands (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    guild_id BIGINT NOT NULL,
                    command_name TEXT NOT NULL,
                    response TEXT NOT NULL,
                    description TEXT,
                    created_by BIGINT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (guild_id, command_name)
                )
            """)

            # Reaction Roles table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reaction_roles (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    guild_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    role_id BIGINT NOT NULL,
                    emoji TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (message_id, emoji)
                )
            """)

            # Analytics Data table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_data (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    guild_id BIGINT NOT NULL,
                    data_type TEXT NOT NULL,
                    target_id BIGINT NOT NULL,
                    count INTEGER DEFAULT 0,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    additional_data JSONB,
                    INDEX (guild_id, data_type, target_id)
                )
            """)

    # Warning Methods
    async def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
                VALUES ($1, $2, $3, $4)
            """, guild_id, user_id, moderator_id, reason)
            
            # Get warning count
            return await conn.fetchval("""
                SELECT COUNT(*) FROM warnings
                WHERE guild_id = $1 AND user_id = $2
            """, guild_id, user_id)

    async def get_warnings(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT * FROM warnings
                WHERE guild_id = $1 AND user_id = $2
                ORDER BY timestamp DESC
            """, guild_id, user_id)

    # Analytics Methods
    async def log_activity(self, guild_id: int, channel_id: int, user_id: int, event_type: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO analytics (guild_id, channel_id, user_id, event_type)
                VALUES ($1, $2, $3, $4)
            """, guild_id, channel_id, user_id, event_type)

    async def get_analytics(self, guild_id: int, timeframe: str) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT 
                    COUNT(*) as message_count,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT channel_id) as active_channels
                FROM analytics
                WHERE guild_id = $1
                AND timestamp > NOW() - $2::interval
            """, guild_id, timeframe)

    # Welcome Settings Methods
    async def set_welcome(self, guild_id: int, channel_id: int, message: str, 
                         dm_message: Optional[str] = None, use_embed: bool = True):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO welcome_settings (guild_id, channel_id, welcome_message, dm_message, use_embed)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (guild_id)
                DO UPDATE SET 
                    channel_id = $2,
                    welcome_message = $3,
                    dm_message = $4,
                    use_embed = $5
            """, guild_id, channel_id, message, dm_message, use_embed)

    async def get_welcome_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT * FROM welcome_settings WHERE guild_id = $1
            """, guild_id)

    # Custom Commands Methods
    async def create_command(self, guild_id: int, command_name: str, 
                           response: str, description: str, created_by: int):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO custom_commands 
                (guild_id, command_name, response, description, created_by)
                VALUES ($1, $2, $3, $4, $5)
            """, guild_id, command_name, response, description, created_by)

    async def get_commands(self, guild_id: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT * FROM custom_commands WHERE guild_id = $1
            """, guild_id)

    # Add methods for reaction roles
    async def add_reaction_role(self, guild_id: int, message_id: int, 
                              channel_id: int, role_id: int, emoji: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO reaction_roles 
                (guild_id, message_id, channel_id, role_id, emoji)
                VALUES ($1, $2, $3, $4, $5)
            """, guild_id, message_id, channel_id, role_id, emoji)

    async def get_reaction_roles(self, guild_id: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT * FROM reaction_roles WHERE guild_id = $1
            """, guild_id)

    # Add methods for analytics
    async def log_analytics(self, guild_id: int, data_type: str, 
                          target_id: int, count: int = 1, 
                          additional_data: dict = None):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO analytics_data 
                (guild_id, data_type, target_id, count, additional_data)
                VALUES ($1, $2, $3, $4, $5)
            """, guild_id, data_type, target_id, count, additional_data)

    async def get_analytics_data(self, guild_id: int, data_type: str, 
                               timeframe: str) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT * FROM analytics_data 
                WHERE guild_id = $1 
                AND data_type = $2
                AND timestamp > NOW() - $3::interval
                ORDER BY timestamp DESC
            """, guild_id, data_type, timeframe)