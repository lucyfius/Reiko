CREATE TABLE IF NOT EXISTS filter_patterns (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    pattern TEXT NOT NULL,
    regex_pattern TEXT,
    severity INT DEFAULT 1,
    description TEXT,
    category TEXT,
    is_regex BOOLEAN DEFAULT false,
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS filter_categories (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    name TEXT,
    severity INT DEFAULT 1,
    action TEXT DEFAULT 'warn',
    UNIQUE(guild_id, name)
);

CREATE TABLE IF NOT EXISTS filter_exemptions (
    guild_id BIGINT,
    type TEXT, -- 'role', 'channel', 'user'
    target_id BIGINT,
    category TEXT,
    UNIQUE(guild_id, type, target_id, category)
);

CREATE TABLE IF NOT EXISTS filter_violations (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    user_id BIGINT,
    channel_id BIGINT,
    message_content TEXT,
    matched_pattern TEXT,
    category TEXT,
    severity INT,
    action_taken TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 