import dataclasses
from typing import Protocol


class InvalidIdentifierError(Exception):
    pass


class PythonType(Protocol):
    def type_hint(self) -> str: ...
    def imports(self) -> list[str]: ...


@dataclasses.dataclass(frozen=True)
class TypedIdentifier:
    _name: str
    _type: PythonType

    def __post_init__(self) -> None:
        if not self._name.isidentifier():
            raise InvalidIdentifierError()

    def type_hint(self) -> str:
        return self._type.type_hint()
    
    def imports(self) -> list[str]:
        return self.type_.imports()
    
    def name(self) -> str:
        return self._name


@dataclasses.dataclass
class StatementTypes:
    arg_types: list[TypedIdentifier]
    return_types: list[TypedIdentifier]
