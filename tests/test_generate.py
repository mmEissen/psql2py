from psql2py import generate, inspect
import pytest


@pytest.fixture
def database_schema(pg_database):
    return inspect.inspect_database(pg_database.connection_kwargs())



