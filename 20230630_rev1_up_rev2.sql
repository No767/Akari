ALTER TABLE tag ALTER COLUMN created_at SET DEFAULT (NOW() AT TIME ZONE 'utc');

CREATE TABLE IF NOT EXISTS tag_lookup (
    id SERIAL PRIMARY KEY,
    name TEXT,
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
CREATE INDEX IF NOT EXISTS tag_lookup_location_id_idx ON tag_lookup (guild_id);
CREATE INDEX IF NOT EXISTS tag_lookup_name_trgm_idx ON tag_lookup USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tag_lookup_name_lower_idx ON tag_lookup (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS tag_lookup_uniq_idx ON tag_lookup (LOWER(name), guild_id);