-- Revises: V0
-- Creation Date: 2023-05-24 19:05:55.776149 UTC
-- Reason: Initial migration

CREATE TABLE IF NOT EXISTS guild (
    id BIGINT PRIMARY KEY NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tag (
    id SERIAL PRIMARY KEY NOT NULL,
    author_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    aliases TEXT[],
    content TEXT NOT NULL,
    created_at timestamp WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_guild FOREIGN KEY (guild_id) REFERENCES guild (id) ON DELETE CASCADE
);
