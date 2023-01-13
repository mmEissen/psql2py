import importlib
import pytest
import tempfile
from os import path
import sys

from psql2py import generate


@pytest.fixture
def simple_module(data_dir: str):
    with tempfile.TemporaryDirectory() as tempdir:
        generate.package_from_dir(path.join(data_dir, "simple_module"), tempdir)
        sys.path.append(tempdir)
        try:
            yield importlib.import_module("simple_module")
        finally:
            sys.path.pop()


def test_simple_select(simple_module, db_connection):
    message = "Hello, world!"

    response = simple_module.simple_select(db_connection, echo=message)

    first_row = list(response)[0]
    assert first_row.echo == message
