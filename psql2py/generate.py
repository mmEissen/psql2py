from __future__ import annotations

import dataclasses
from typing import Iterable, NewType, Type
import sqlparse
import re
import os
from os import path
import pathlib
import jinja2
import docstring_parser
import shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from psql2py import inspect

SQL_EXTENSION = ".sql"
COLUMNS = "\nCOLUMNS:\n"


class WrongNumberOfStatementsInFile(Exception):
    pass


class SqlDirChangeEventHandler(FileSystemEventHandler):
    def __init__(self, root_dir: str, target_dir: str) -> None:
        self.root_dir = root_dir
        self.target_dir = target_dir

    def on_any_event(self, event: object) -> None:
        package_from_dir(self.root_dir, self.target_dir)


def package_from_dir_continuous(dirname: str, output_path: str) -> None:
    observer = Observer()
    event_handler = SqlDirChangeEventHandler(dirname, output_path)
    observer.schedule(event_handler, dirname, recursive=True)
    observer.start()

    try:
        input("Press enter to stop")
    finally:
        observer.stop()
        observer.join()


def _is_arg_placeholder(token: sqlparse.sql.Token) -> bool:
    return token.ttype == sqlparse.tokens.Token.Name.Placeholder and bool(
        re.match(r"%\(\w+\)s", token.value)
    )


def _args_from_statement(sql_statement: str) -> list[str]:
    parsed: sqlparse.sql.Statement = sqlparse.parse(sql_statement)[0]
    placeholder_names = [
        token.value[2:-2] for token in parsed.flatten() if _is_arg_placeholder(token)
    ]
    return sorted(set(placeholder_names))


def render_module(statements: list[Statement]) -> str:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("psql2py", "templates"),
    )
    template = env.get_template("module.py.jinja")
    return template.render({"statements": statements})


def package_from_statement_dir(statement_dir: StatementDir, output_path: str) -> None:
    output_path = path.join(output_path, statement_dir.name)
    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
    with open(path.join(output_path, "__init__.py"), "w") as out_file:
        out_file.write(render_module(statement_dir.statements))
    for sub_dir in statement_dir.sub_dirs:
        package_from_statement_dir(
            sub_dir,
            output_path,
        )


def package_from_dir(dirname: str, output_path: str) -> None:
    statement_dir = load_dir(dirname)
    shutil.rmtree(output_path)
    package_from_statement_dir(statement_dir, output_path)


def get_docstring_comment(sql_statement: str) -> str:
    parsed: sqlparse.sql.Statement = sqlparse.parse(sql_statement)[0]
    first_token = next(parsed.flatten())
    if first_token.ttype == sqlparse.tokens.Token.Comment.Multiline:
        docstring = first_token.value[2:-2].strip()
        return docstring
    return ""


def get_docstring(sql_statement: str) -> str:
    docstring_comment = get_docstring_comment(sql_statement)
    return docstring_comment.split(COLUMNS)[0]


def get_columns_comment(sql_statement: str) -> str:
    docstring_comment = get_docstring_comment(sql_statement)
    try:
        return docstring_comment.split(COLUMNS)[1]
    except IndexError:
        return ""


def get_types_from_docstring(docstring: str) -> dict[str, str]:
    parsed = docstring_parser.parse(docstring)
    return {
        param.arg_name: param.type_name
        for param in parsed.params
    }


def get_returned_columns(sql_statement: str) -> list[ColumnType] | None:
    columns_comment =  get_columns_comment(sql_statement)
    if not columns_comment:
        return None
    lines = columns_comment.split("\n")
    def line_to_column_type(line: str) -> ColumnType:
        name, type_ = line.split(":")
        return ColumnType(name.strip(), type_.strip())
    return [line_to_column_type(line) for line in lines if line.strip()]


def load_file(filename: str) -> Statement:
    with open(filename, "r") as sql_file:
        content = sql_file.read()
    sql_statements = sqlparse.split(content)
    if len(sql_statements) != 1:
        raise WrongNumberOfStatementsInFile()
    sql_statement = sql_statements[0]
    arg_names = _args_from_statement(sql_statement)
    docstring = get_docstring(sql_statement)
    types_from_docstring = get_types_from_docstring(docstring)
    returned_columns = get_returned_columns(sql_statement)
    function_name = path.splitext(path.basename(filename))[0]
    return Statement(
        function_name,
        sql_statement,
        docstring=docstring,
        column_types=returned_columns,
        args=[StatementArg(name, types_from_docstring.get(name)) for name in arg_names],
    )


def load_dir(dirname: str) -> StatementDir:
    filenames = [os.path.join(dirname, filename) for filename in os.listdir(dirname)]
    sql_files = [
        filename
        for filename in filenames
        if os.path.isfile(filename) and filename.endswith(SQL_EXTENSION)
    ]
    sub_dirs = [filename for filename in filenames if os.path.isdir(filename)]
    return StatementDir(
        name=os.path.basename(dirname),
        statements=[load_file(filename) for filename in sql_files],
        sub_dirs=[load_dir(dirname) for dirname in sub_dirs],
    )


@dataclasses.dataclass
class StatementDir:
    name: str
    statements: list[Statement]
    sub_dirs: list[StatementDir] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Statement:
    function_name: str
    sql: str
    docstring: str = ""
    column_types: list[ColumnType] | None = None
    args: list[StatementArg] | None = None

    def row_name(self) -> str:
        return "".join(word.title() for word in self.function_name.split("_")) + "Row"


@dataclasses.dataclass
class ColumnType:
    name: str
    type_: str


@dataclasses.dataclass
class StatementArg:
    name: str
    type_: str | None = None
