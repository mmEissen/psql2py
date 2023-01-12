from __future__ import annotations

import dataclasses
import itertools
from typing import Any

import psycopg2


@dataclasses.dataclass
class Database:
    schemas: dict[str, Schema] = dataclasses.field(default_factory=dict)
    search_path = ("public",)


@dataclasses.dataclass
class Schema:
    name: str
    tables: dict[str, Table] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Table:
    name: str
    columns: dict[str, Column] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Column:
    name: str
    postgres_type: str
    is_nullable: bool


@dataclasses.dataclass
class ColumnResult:
    table_schema: str
    table_name: str
    column_name: str
    data_type: str
    is_nullable: str


def inspect_database(connection_params: dict[str, Any]) -> Database:
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 
            table_schema, 
            table_name, 
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, column_name
        """
    )

    all_columns = [ColumnResult(*row) for row in cursor.fetchall()]

    return Database(
        schemas={
            schema_name: Schema(
                name=schema_name,
                tables={
                    table_name: Table(
                        name=table_name,
                        columns={
                            column.column_name: Column(
                                name=column.column_name,
                                postgres_type=column.data_type,
                                is_nullable=column.is_nullable == "YES",
                            )
                            for column in columns_in_table
                        },
                    )
                    for table_name, columns_in_table in itertools.groupby(
                        columns_in_schema,
                        key=lambda column_result: column_result.table_name,
                    )
                },
            )
            for schema_name, columns_in_schema in itertools.groupby(
                all_columns, key=lambda column_result: column_result.table_schema
            )
        },
    )

