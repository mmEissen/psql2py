/* This is the docstring

This is more docstring.

:param int min_age:

COLUMNS:
id: int
name: str
age: int
*/

select 
    id,
    name,
    age
from user where age > %(min_age)s