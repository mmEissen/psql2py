from __future__ import annotations

from typing import Iterable
import psycopg2


def execute(connection: "psycopg2.connection", statement: str, values: dict[str, object]) -> Iterable[tuple[object, ...]]:
    cursor = connection.cursor()
    cursor.execute(statement, values)
    yield from cursor
