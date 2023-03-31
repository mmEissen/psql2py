from os import path
import pytest
from psql2py import load, inspect, render


class TestLoadFile:
    @pytest.fixture
    def query_sql_path(self, module_data_dir):
        return path.join(module_data_dir, "query.sql")


    def test_happy_path(self, query_sql_path):
        statement = load.load_file(query_sql_path)

        assert statement.name == "query"
        assert statement.arg_names == ["kingdom_name"]
        assert statement.docstring == "I am the docstring!"
        assert statement.sql


class TestLoadDirRecursive:
    @pytest.fixture
    def root_dir_path(self, module_data_dir):
        return path.join(module_data_dir, "root_dir")

    def test_happy_path(self, root_dir_path):
        statement_dir = load.load_dir_recursive(root_dir_path)

        assert statement_dir.name == "root_dir"
        assert not statement_dir.statements
        assert len(statement_dir.sub_dirs) == 1
        sub_dir = statement_dir.sub_dirs[0]
        assert sub_dir.name == "sub_dir"
        assert {statement.name for statement in sub_dir.statements} == {"sub_query_1", "sub_query_2"}


class TestStatementDirToPackageOrModule:
    @pytest.fixture
    def dir_name(self):
        return "root_dir"
    
    @pytest.fixture()
    def root_dir_path(self, module_data_dir, dir_name):
        return path.join(module_data_dir, dir_name)
    
    @pytest.fixture
    def statement_dir(self, root_dir_path):
        return load.load_dir_recursive(root_dir_path)
    
    @pytest.fixture
    def inference_func(self, db_connection):
        return lambda statement: inspect.infer_types(statement, db_connection)
    
    @pytest.mark.parametrize(
            "dir_name", ["example_package"]
    )
    def test_happy_path_package(self, statement_dir, inference_func):
        package_or_module = statement_dir.to_package_or_module(inference_func)

        assert isinstance(package_or_module, render.Package)
        assert len(package_or_module.sub_modules) == 1
        sub_module = package_or_module.sub_modules[0]
        assert sub_module.name == "sub_module"
    
    @pytest.mark.parametrize(
            "dir_name", ["example_module"]
    )
    def test_happy_path_module(self, statement_dir, inference_func):
        package_or_module = statement_dir.to_package_or_module(inference_func)

        assert isinstance(package_or_module, render.Module)
        assert package_or_module.name == "example_module"
