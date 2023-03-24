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
def data_dir():
    return DATA_DIR


@pytest.fixture(scope="module")
def module_data_dir(data_dir, request):
    module_name, _ = path.splitext(request.node.name)
    common_path = path.commonprefix(["tests/", module_name])
    path_from_data_dir = module_name[len(common_path):]
    return path.join(data_dir, path_from_data_dir)


@pytest.fixture(scope="session")
def pg_setup_db():
    return setup_db


@pytest.fixture
def db_connection(pg_database: pg_docker.DatabaseParams):
    connection = psycopg2.connect(**pg_database.connection_kwargs())
    try:
        yield connection
    finally:
        connection.close()
