from __future__ import annotations

import pytest
import pg_docker
import psycopg2

from os import path

pytest_plugins = ["pg_docker"]


DATA_DIR = path.join(path.dirname(__file__), "data")
TEST_SCHEMA = path.join(DATA_DIR, "test_schema.sql")


def setup_db(pg_params: pg_docker.DatabaseParams):
    with open(TEST_SCHEMA) as schema_file:
        sql_statements = [
            statement
            for statement in schema_file.read().split(";")
            if statement.strip()
        ]

    try:
        cursor = psycopg2.connect(**pg_params.connection_kwargs()).cursor()
        cursor.execute("COMMIT")
        for statement in sql_statements:
            cursor.execute(statement)
        cursor.close()
        cursor.connection.close()
    except psycopg2.OperationalError:
        pass


@pytest.fixture(scope="session")
def pg_setup_db():
    return setup_db


@pytest.fixture
def db_cursor(pg_database: pg_docker.DatabaseParams):
    cursor = psycopg2.connect(**pg_database.connection_kwargs()).cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        cursor.connection.close()
