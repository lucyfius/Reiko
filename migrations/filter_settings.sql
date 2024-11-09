CREATE TABLE IF NOT EXISTS filter_settings (
    guild_id BIGINT PRIMARY KEY,
    filter_action TEXT DEFAULT 'warn',
    notify_channel BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS filter_violations (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    user_id BIGINT,
    channel_id BIGINT,
    severity INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 