from os import path
import pytest
from psql2py import load, inspect


class TestInferTypes:
    @pytest.fixture
    def query_file_name(self):
        return "query.sql"


    @pytest.fixture
    def query_path(self, query_file_name, module_data_dir):
        return path.join(module_data_dir, query_file_name)


    @pytest.fixture
    def statement(self, query_path):
        return load.load_file(query_path)


    def test_happy_path(self, statement, db_connection, pg_database):
        result = inspect.infer_types(statement, db_connection)

        assert [arg_type.type_hint() for arg_type in result.arg_types] == ["list[int]", "str"]
        assert [return_type.name() for return_type in result.return_types] == ["kingdom_id", "name"]
        assert [return_type.type_hint() for return_type in result.return_types] == ["int", "str"]


    @pytest.mark.parametrize(
            "query_file_name", ["select_1.sql"]
    )
    def test_no_query_params(self, statement, db_connection, pg_database):
        result = inspect.infer_types(statement, db_connection)

        assert result.arg_types == []
        assert [return_type.type_hint() for return_type in result.return_types] == ["int"]
    
    @pytest.mark.parametrize(
            "query_file_name", ["insert.sql"]
    )
    def test_insert_query_with_hints(self, statement, db_connection, pg_database):
        result = inspect.infer_types(statement, db_connection)

        assert [arg_type.type_hint() for arg_type in result.arg_types] == ["str"]
        assert [arg_type.name() for arg_type in result.arg_types] == ["name"]
        assert [return_type.name() for return_type in result.return_types] == ["kingdom_id"]
        assert [return_type.type_hint() for return_type in result.return_types] == ["int"]
