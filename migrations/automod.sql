CREATE TABLE IF NOT EXISTS automod_settings (
    guild_id BIGINT PRIMARY KEY,
    spam_threshold INT DEFAULT 5,
    spam_window_seconds INT DEFAULT 5,
    max_mentions INT DEFAULT 5,
    link_filter BOOLEAN DEFAULT false,
    caps_threshold INT DEFAULT 70,
    warn_threshold INT DEFAULT 3,
    action_type TEXT DEFAULT 'warn',
    exempt_roles BIGINT[] DEFAULT ARRAY[]::BIGINT[],
    exempt_channels BIGINT[] DEFAULT ARRAY[]::BIGINT[]
);

CREATE TABLE IF NOT EXISTS automod_logs (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    user_id BIGINT,
    action_type TEXT,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS automod_whitelist (
    guild_id BIGINT,
    item TEXT,
    type TEXT, -- 'link', 'word', etc.
    added_by BIGINT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (guild_id, item, type)
); 