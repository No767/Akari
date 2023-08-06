CREATE TABLE IF NOT EXISTS guild (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tag (
    id SERIAL PRIMARY KEY,
    author_id BIGINT,
    name VARCHAR(255),
    content TEXT,
    created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),
    guild_id BIGINT REFERENCES guild (id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS tag_lookup (
    id SERIAL PRIMARY KEY,
    name TEXT,
    aliases TEXT[],
    guild_id BIGINT,
    owner_id BIGINT,
    created_at TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc'),
    tag_id INTEGER REFERENCES tag (id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS tag_name_idx ON tag (name);
CREATE INDEX IF NOT EXISTS tag_name_trgm_idx ON tag USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tag_name_lower_idx ON tag (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS tag_uniq_idx ON tag (LOWER(name), guild_id);

CREATE INDEX IF NOT EXISTS tag_lookup_name_idx ON tag_lookup (name);
CREATE INDEX IF NOT EXISTS tag_lookup_aliases_idx ON tag_lookup USING GIN (aliases);
CREATE INDEX IF NOT EXISTS tag_lookup_location_id_idx ON tag_lookup (guild_id);
CREATE INDEX IF NOT EXISTS tag_lookup_name_trgm_idx ON tag_lookup USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tag_lookup_name_lower_idx ON tag_lookup (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS tag_lookup_uniq_idx ON tag_lookup (LOWER(name), guild_id);