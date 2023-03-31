import importlib
from os import path
import sys
import tempfile
import pytest


from psql2py import generate, core


class TestPackageFromDir:
    @pytest.fixture
    def dir_name(self):
        return "example_module"
    
    @pytest.fixture()
    def input_dir_path(self, module_data_dir, dir_name):
        return path.join(module_data_dir, dir_name)

    @pytest.fixture()
    def output_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            sys.path.append(temp_dir)
            yield temp_dir
            sys.path.pop()

    @pytest.fixture
    def connection_factory(self, db_connection):
        return lambda: db_connection
    
    @pytest.fixture(autouse=True)
    def core_connection_factory(self, pg_database):
        core.set_connection_manager_from_kwargs(pg_database.connection_kwargs())
    
    def test_happy_path(self, output_dir, connection_factory, input_dir_path):
        generate.package_from_dir(input_dir_path, output_dir, connection_factory)

        module = importlib.import_module("example_module")
        assert "query" in [name for name in dir(module) if not name.startswith("__")]
        rows = module.query()
        assert len(rows) == 1
        row = rows[0]
        assert row.one == 1

