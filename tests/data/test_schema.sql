CREATE TABLE hero (
    hero_id BIGINT PRIMARY KEY,
    name text NOT NULL,
    companion BIGINT REFERENCES hero(hero_id)
);

CREATE TABLE kingdom (
    kingdom_id BIGINT PRIMARY KEY,
    name text NOT NULL,
    ruler BIGINT REFERENCES hero(hero_id)
);
