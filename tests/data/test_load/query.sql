/* I am the docstring! */

SELECT * 
FROM kingdom
WHERE name = %(kingdom_name)
AND kingdom_id in %(kingdom_ids)
