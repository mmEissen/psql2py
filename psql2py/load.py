from __future__ import annotations

import dataclasses
import os
import re
from typing import Callable

import sqlparse

from psql2py import render, common


SQL_EXTENSION = ".sql"


class WrongNumberOfStatementsInFile(Exception):
    pass


class InvalidDirectoryStructure(Exception):
    pass


class InvalidFileName(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class StatementDir:
    name: str
    statements: tuple[Statement]
    sub_dirs: tuple[StatementDir]

    def __post_init__(self) -> None:
        if not self.name.isidentifier():
            raise InvalidFileName(f"The file {self.name} is not a valid identifier")
        if self.statements and self.sub_dirs:
            raise InvalidDirectoryStructure()

    def _to_package(
        self, inference_func: Callable[[Statement], common.StatementTypes]
    ) -> render.Package:
        assert not self.statements

        sub_packages_or_modules: list[render.Package | render.Module] = [
            sub_dir.to_package_or_module(inference_func) for sub_dir in self.sub_dirs
        ]
        sub_packages = [
            package_or_module
            for package_or_module in sub_packages_or_modules
            if package_or_module.is_package()
        ]
        sub_modules = [
            package_or_module
            for package_or_module in sub_packages_or_modules
            if package_or_module.is_module()
        ]

        return render.Package(
            self.name, sub_packages, sub_modules
        )

    def _to_module(
        self, inference_func: Callable[[Statement], common.StatementTypes]
    ) -> render.Package:
        assert not self.sub_dirs

        types = [inference_func(statement) for statement in self.statements]

        return render.Module(self.name, [
                render.TypedStatement(
                    statement.name,
                    statement.docstring,
                    statement.sql,
                    types_.arg_types,
                    types_.return_types,
                )
                for statement, types_ in zip(self.statements, types)
            ]
        )

    def to_package_or_module(
        self, inference_func: Callable[[Statement], common.StatementTypes]
    ) -> render.Package | render.Module:
        if self.sub_dirs:
            return self._to_package(inference_func)
        return self._to_module(inference_func)


@dataclasses.dataclass
class Statement:
    name: str
    sql: str
    arg_names: list[str]
    docstring: str = ""

    def row_name(self) -> str:
        return "".join(word.title() for word in self.name.split("_")) + "Row"


def load_dir_recursive(dirname: str) -> StatementDir:
    filenames = [os.path.join(dirname, filename) for filename in os.listdir(dirname)]
    sql_files = [
        filename
        for filename in filenames
        if os.path.isfile(filename) and filename.endswith(SQL_EXTENSION)
    ]
    sub_dirs = [filename for filename in filenames if os.path.isdir(filename)]
    return StatementDir(
        name=os.path.basename(dirname),
        statements=tuple(load_file(filename) for filename in sql_files),
        sub_dirs=tuple(load_dir_recursive(dirname) for dirname in sub_dirs),
    )


def load_file(filename: str) -> Statement:
    with open(filename, "r") as sql_file:
        content = sql_file.read()
    sql_statements = sqlparse.split(content)

    if len(sql_statements) != 1:
        raise WrongNumberOfStatementsInFile()

    sql_statement = sql_statements[0]
    arg_names = _args_from_statement(sql_statement)
    docstring = _get_docstring(sql_statement)
    function_name = os.path.splitext(os.path.basename(filename))[0]

    return Statement(
        name=function_name, sql=sql_statement, docstring=docstring, arg_names=arg_names
    )


def _args_from_statement(sql_statement: str) -> list[str]:
    parsed: sqlparse.sql.Statement = sqlparse.parse(sql_statement)[0]
    placeholder_names = [
        token.value[2:-2] for token in parsed.flatten() if _is_arg_placeholder(token)
    ]
    return sorted(set(placeholder_names))


def _get_docstring(sql_statement: str) -> str:
    parsed: sqlparse.sql.Statement = sqlparse.parse(sql_statement)[0]
    first_token = next(parsed.flatten())
    if first_token.ttype == sqlparse.tokens.Token.Comment.Multiline:
        docstring = first_token.value[2:-2].strip()
        return docstring
    return ""


def _is_arg_placeholder(token: sqlparse.sql.Token) -> bool:
    return token.ttype == sqlparse.tokens.Token.Name.Placeholder and bool(
        re.match(r"%\(\w+\)s", token.value)
    )
