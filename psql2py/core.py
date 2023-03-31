from __future__ import annotations

from typing import ContextManager

import contextlib
import psycopg2
import psycopg2.extensions


class ConnectionFactoryNotSet(Exception):
    pass


@contextlib.contextmanager
def _not_set() -> psycopg2.extensions.connection:
    raise ConnectionFactoryNotSet()


_connection_factory: ContextManager[psycopg2.extensions.connection] = _not_set


def execute(statement: str, values: dict[str, object]) -> list[tuple[object, ...]]:
    with _connection_factory() as connection, connection.cursor() as cursor:
        cursor.execute(statement, values)
        return cursor.fetchall()


def set_connection_manager(manager: ContextManager[psycopg2.extensions.connection]) -> None:
    global _connection_factory
    _connection_factory = manager


def set_connection_manager_from_kwargs(kwargs: dict[str, object]) -> None:
    @contextlib.contextmanager
    def _manager():
        connection = psycopg2.connect(**kwargs)
        try:
            yield connection
        except Exception:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()
    set_connection_manager(_manager)
