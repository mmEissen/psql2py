import dataclasses
from typing import Protocol



class PythonType(Protocol):
    def type_hint(self) -> str: ...
    def imports(self) -> list[str]: ...


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
    _item_type: PythonType

    def type_hint(self) -> str:
        return f"list[{self._item_type.type_hint()}]"
    
    def imports(self) -> list[str]:
        return self._item_type.imports()


PY_BOOL = PythonBaseType("bool")
PY_INT = PythonBaseType("int")
PY_FLOAT = PythonBaseType("float")
PY_DECIMAL = PythonBaseType("decimal.Decimal", "decimal")
PY_STR = PythonBaseType("str")

PY_OBJECT = PythonBaseType("object")


MAPPING = {
    "boolean": PY_BOOL,
    "real": PY_FLOAT,
    "double": PY_FLOAT,
    "smallint": PY_INT,
    "integer": PY_INT,
    "bigint": PY_INT,
    "numeric": PY_DECIMAL,
    "text": PY_STR,
}


def pg_to_py(pg_type: str) -> PythonType:
    if pg_type.endswith("[]"):
        return PythonListType(pg_to_py(pg_type[:-2]))
    return MAPPING.get(pg_type, PY_OBJECT)
