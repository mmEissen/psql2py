from typing import (
    Any,
    Iterable,
    overload,
)
from psql2py import core
import psycopg2
import dataclasses



_another_query_STATEMENT = r"""
/*  */

SELECT * from foo
"""

AnotherQueryRow = tuple

@overload
def another_query(
    connection: psycopg2.connection,
) -> Iterable[AnotherQueryRow]:
    ...

def another_query(connection, **kwargs):
    """
    """
    return AnotherQueryRow(*core.execute(connection, _another_query_STATEMENT, **kwargs))



_simple_select_STATEMENT = r"""
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
"""

@dataclasses.dataclass
class SimpleSelectRow:
    id: int
    name: str
    age: int

@overload
def simple_select(
    connection: psycopg2.connection,
    *,
    min_age: int,
) -> Iterable[SimpleSelectRow]:
    ...

def simple_select(connection, **kwargs):
    """This is the docstring

    This is more docstring.

    :param int min_age:

    """
    return SimpleSelectRow(*core.execute(connection, _simple_select_STATEMENT, **kwargs))


