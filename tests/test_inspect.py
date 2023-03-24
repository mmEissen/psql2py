from os import path
import pytest
from psql2py import load, inspect


class TestInferTypes:
    @pytest.fixture
    def query_path(self, module_data_dir):
        return path.join(module_data_dir, "query.sql")


    @pytest.fixture
    def statement(self, query_path):
        return load.load_file(query_path)


    def test_happy_path(self, statement, db_connection, pg_database):
        result = inspect.infer_types(statement, db_connection)

        assert [arg_type.type_hint() for arg_type in result.arg_types] == ["list[int]", "str"]
        assert [return_type.pg_name for return_type in result.return_types] == ["kingdom_id", "name"]
        assert [return_type.type_hint() for return_type in result.return_types] == ["int", "str"]
