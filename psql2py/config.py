from __future__ import annotations

import pydantic
import tomllib

_TOOL = "tool"
_TOOL_NAME = "psql2py"

_config: Config | None = None


class ConfigNotLoaded(Exception):
    pass


class Config(pydantic.BaseModel):
    source_directory: str
    output_directory: str


def load_config(filename: str) -> None:
    global _config
    
    with open(filename, "rb") as conf_file:
        data = tomllib.load(conf_file).get(_TOOL, {}).get(_TOOL_NAME)
    _config = Config(
        source_directory=data["source_directory"],
        output_directory=data["output_directory"],
    )


def config() -> Config:
    if _config is None:
        raise ConfigNotLoaded
    return _config
