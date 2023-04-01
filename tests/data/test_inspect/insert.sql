/*
Columns:
    kingdom_id: bigint
*/

INSERT INTO kingdom (name) VALUES (%(name)s) RETURNING kingdom_id