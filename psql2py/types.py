from __future__ import annotations

from psql2py import common

import dataclasses
import logging

log = logging.getLogger(__name__)

@dataclasses.dataclass(frozen=True)
class PythonBaseType:
    _type_hint: str
    _import: str | None = None

    def type_hint(self) -> str:
        return self._type_hint

    def imports(self) -> list[str]:
        return [self._import] if self._import is not None else []


@dataclasses.dataclass(frozen=True)
class PythonListType:
    _item_type: common.PythonType

    def type_hint(self) -> str:
        return f"list[{self._item_type.type_hint()}]"
    
    def imports(self) -> list[str]:
        return self._item_type.imports()


@dataclasses.dataclass(frozen=True)
class PythonUnionType:
    _left: common.PythonType
    _right: common.PythonType

    def type_hint(self) -> str:
        return f"{self._left.type_hint()} | {self._right.type_hint()}"


PY_NONE = PythonBaseType("None")
PY_BOOL = PythonBaseType("bool")
PY_INT = PythonBaseType("int")
PY_FLOAT = PythonBaseType("float")
PY_DECIMAL = PythonBaseType("decimal.Decimal", "decimal")
PY_STR = PythonBaseType("str")
PY_DATETIME = PythonBaseType("datetime.datetime", "datetime")

PY_OBJECT = PythonBaseType("object")


MAPPING = {
    "null": PY_NONE,
    "boolean": PY_BOOL,
    "real": PY_FLOAT,
    "double": PY_FLOAT,
    "smallint": PY_INT,
    "integer": PY_INT,
    "bigint": PY_INT,
    "numeric": PY_DECIMAL,
    "text": PY_STR,
    "timestamp without time zone": PY_DATETIME,
}


def pg_to_py(pg_type: str, is_nullable: bool=False) -> common.PythonType:
    if is_nullable:
        return PythonUnionType(pg_to_py(pg_type, is_nullable=False), PY_NONE)
    if pg_type.endswith("[]"):
        return PythonListType(pg_to_py(pg_type[:-2]))
    try:
        return MAPPING[pg_type]
    except KeyError:
        log.warning("Could not map pg type '%s' to python type", pg_type)
        return PY_OBJECT
