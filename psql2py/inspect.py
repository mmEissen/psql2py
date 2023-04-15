from __future__ import annotations
import itertools
import re

import psycopg2
import psycopg2.extensions

from psql2py import load, types, common


_sequence = itertools.count()
def _unique_int() -> int:
    return next(_sequence)


def infer_types(statement: load.Statement, db_connection: psycopg2.extensions.connection) -> common.StatementTypes:
    arg_types = _infer_arg_types(statement, db_connection)
    return_types = _infer_return_types(statement, db_connection)

    return common.StatementTypes(
        arg_types,
        return_types,
    )


def _infer_arg_types(statement: load.Statement, db_connection: psycopg2.extensions.connection) -> list[common.TypedIdentifier]:
    """Use a prepared statement and then query pg_prepared_statements https://www.postgresql.org/docs/current/view-pg-prepared-statements.html"""
    
    if not statement.arg_names:
        return []

    query = statement.sql
    for i, arg_name in enumerate(statement.arg_names, start=1):
        query = query.replace(f"%({arg_name})s", f"${i}")

    with db_connection.cursor() as cursor:
        cursor.execute("PREPARE query (unknown) AS " + query)
        cursor.execute(
            "SELECT unnest(parameter_types) FROM pg_prepared_statements WHERE name = 'query'"
        )
        pg_types = [row[0] for row in cursor.fetchall()]
        cursor.execute("DEALLOCATE query")
    return [
        common.TypedIdentifier(
            name,
            types.pg_to_py(pg_type)
        )
        for name, pg_type in zip(statement.arg_names, pg_types)
    ]


def _return_type_from_docstring(statement: load.Statement) -> list[common.TypedIdentifier] | None:
    column_hints = re.match(r"^Columns:\n((\W+(\w+: \w+$))+)", statement.docstring)
    if not column_hints:
        return None
    hints = [hint.strip().split(": ") for hint in column_hints.group(1).split("\n")]
    return [
        common.TypedIdentifier(
            name,
            types.pg_to_py(pg_type),
        )
        for name, pg_type in hints
    ]


def _infer_return_types(statement: load.Statement, db_connection: psycopg2.extensions.connection) -> list[common.TypedIdentifier]:
    """https://stackoverflow.com/questions/57335039/get-postgresql-resultset-column-types-without-executing-query-using-psycopg2"""
    docstring_hints = _return_type_from_docstring(statement)
    if docstring_hints is not None:
        return docstring_hints

    with db_connection.cursor() as cursor:
        view_number = _unique_int()
        cursor.execute(
            f"CREATE OR REPLACE TEMP VIEW infer_return_{view_number} AS {statement.sql}",
            vars={arg_name: None for arg_name in statement.arg_names}
        )
        # Maybe replace this with a query to pg_attribute: https://www.postgresql.org/docs/current/catalog-pg-attribute.html
        cursor.execute(f"""
            SELECT column_name::text, data_type::text
            FROM information_schema.columns WHERE table_name = 'infer_return_{view_number}'
            ORDER BY ordinal_position
        """)
        return_types = cursor.fetchall()
    return [
        common.TypedIdentifier(
            name,
            types.pg_to_py(return_type),
        )
        for name, return_type in return_types
    ]


