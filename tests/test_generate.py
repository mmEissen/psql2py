from psql2py import generate, inspect
import pytest


@pytest.fixture
def database_schema(pg_database):
    return inspect.inspect_database(pg_database.connection_kwargs())


@pytest.mark.parametrize(
    "statement",
    [
        "SELECT name FROM users;"
    ]
)
def test_function_from_statement(snapshot, statement: str) -> None:
    py_code = generate.function_from_statement("some_function_name", statement)

    snapshot.assert_match(py_code)

