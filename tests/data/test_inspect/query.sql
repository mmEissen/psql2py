/* I am the docstring! */

SELECT kingdom_id, name
FROM kingdom
WHERE name = %(kingdom_name)s
AND kingdom_id = ANY (%(kingdom_ids)s)
