from __future__ import annotations

import dataclasses
import os
import re

import sqlparse


SQL_EXTENSION = ".sql"



class WrongNumberOfStatementsInFile(Exception):
    pass


@dataclasses.dataclass
class StatementDir:
    name: str
    statements: list[Statement]
    sub_dirs: list[StatementDir] = dataclasses.field(default_factory=list)


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
        statements=[load_file(filename) for filename in sql_files],
        sub_dirs=[load_dir_recursive(dirname) for dirname in sub_dirs],
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
        name=function_name,
        sql=sql_statement,
        docstring=docstring,
        arg_names=arg_names
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

