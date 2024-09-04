import dataclasses
import pathlib
import typing as t


@dataclasses.dataclass
class LocLine:
    identifier: str
    text: str


@dataclasses.dataclass
class LocFile:
    sourcefile: pathlib.Path
    language: str
    lines: list[LocLine]


LocId: t.TypeAlias = str
LangId: t.TypeAlias = str
Text: t.TypeAlias = str


@dataclasses.dataclass
class LocalisationData:
    language: str
    entries: dict[LocId, Text] = dataclasses.field(default_factory=dict)
