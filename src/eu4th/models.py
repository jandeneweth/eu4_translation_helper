import dataclasses
import enum
import pathlib
import typing as t

LocId: t.TypeAlias = str
LangId: t.TypeAlias = str
Text: t.TypeAlias = str


# Localisation files


@dataclasses.dataclass
class LocLine:
    identifier: LocId
    text: Text


@dataclasses.dataclass
class LocFile:
    sourcefile: pathlib.Path
    language: LangId
    lines: list[LocLine]


@dataclasses.dataclass
class LocalisationData:
    language: LangId
    entries: dict[LocId, Text] = dataclasses.field(default_factory=dict)


# Translation TSV


class TranslationStatus(enum.Enum):
    MISSING = "missing"
    OUTDATED = "outdated"
    DONE = "done"


@dataclasses.dataclass
class TranslationEntry:
    reference: Text
    translation: Text
    status: TranslationStatus


@dataclasses.dataclass
class TranslationData:
    reference_language: LangId
    translation_language: LangId
    entries: dict[LocId, TranslationEntry] = dataclasses.field(default_factory=dict)
