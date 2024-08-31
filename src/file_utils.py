import collections
import csv
import dataclasses
import logging
import pathlib
import re
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
    languages: set[LangId] = dataclasses.field(default_factory=set)
    entries: dict[LocId, dict[LangId, Text]] = dataclasses.field(default_factory=lambda: collections.defaultdict(dict))


_LOC_LANG_RE = re.compile(r"^l_([a-z]+):$")
_LOC_SEPARATOR_RE = re.compile(r":[0-9]")


def _load_loc_from_file(filepath: pathlib.Path) -> LocFile | None:
    lines = []
    with open(filepath, "r", encoding="utf-8-sig") as fh:
        # Get the language
        language_raw = fh.readline().strip()
        language_match = _LOC_LANG_RE.match(language_raw)
        if not language_match:
            logging.warning(f"Could not find language from file {filepath.name!r}")
            return
        language = language_match.group(1)
        # Parse lines
        for line_nr, line in enumerate(fh, start=2):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                identifier, text = _LOC_SEPARATOR_RE.split(line, maxsplit=1)
            except ValueError:
                logging.warning(f"Invalid entry in localisation file {filepath.name!r}, line {line_nr}")
                continue
            else:
                text = text.strip().removeprefix('"').removesuffix('"').replace('\\"', '"')
                lines.append(
                    LocLine(
                        identifier=identifier.strip(),
                        text=text.strip(),
                    )
                )
    return LocFile(sourcefile=filepath, language=language, lines=lines)


def _merge_localisations(locfiles: list[LocFile]) -> LocalisationData:
    locdata = LocalisationData()
    for locfile in locfiles:
        locdata.languages.add(locfile.language)
        for locline in locfile.lines:
            if locfile.language in locdata.entries[locline.identifier]:
                logging.warning(
                    f"Skipping duplicate definition of {locline.identifier!r} in language {locfile.language!r}"
                )
                continue
            locdata.entries[locline.identifier][locfile.language] = locline.text
    return locdata


def parse_localisation_from_locfiles(dirpath: pathlib.Path, exclude_patterns: list[str]) -> LocalisationData:
    locfiles = []
    exclude_patterns_re = [re.compile(raw) for raw in exclude_patterns]
    for filepath in dirpath.iterdir():
        if not filepath.is_file():
            continue
        if any(pattern.match(str(filepath)) for pattern in exclude_patterns_re):
            continue
        locfile = _load_loc_from_file(filepath=filepath)
        if locfile is not None:
            locfiles.append(locfile)
    return _merge_localisations(locfiles=locfiles)


def parse_localisation_from_tsv(filepath: pathlib.Path) -> LocalisationData:
    locdata = LocalisationData()
    with open(filepath, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(
            fh,
            delimiter="\t",
        )
        locdata.languages.update(name for name in reader.fieldnames if name != "identifier")
        for entry in reader:
            identifier = entry["identifier"]
            for language in locdata.languages:
                locdata.entries[identifier][language] = entry[language]
    return locdata


def write_localisation_to_locfiles(loc_dir: pathlib.Path, locdata: LocalisationData, reference_language: str):
    """Write language localisations to files, except the reference language"""
    output_languages = sorted(lang for lang in locdata.languages if lang != reference_language)
    logging.info(
        f"Writing localisation files for languages: {','.join(output_languages)} "
        f"(ignoring reference language {reference_language!r})"
    )
    for lang in output_languages:
        filepath = loc_dir / f"all_l_{lang}.yml"
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(f"l_{lang}:\n")
            for identifier, lang_text_map in locdata.entries.items():
                if text := lang_text_map[lang]:
                    text = text.replace('"', '\\"')
                    fh.write(f' {identifier}:0 "{text}"\n')


def write_localisation_to_tsv(outpath: pathlib.Path, locdata: LocalisationData, reference_language: str):
    output_languages = sorted(lang for lang in locdata.languages if lang != reference_language)
    with open(outpath, "w", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["identifier", reference_language, *output_languages],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        for identifier, lang_text_map in locdata.entries.items():
            entry_dict = {"identifier": identifier}
            entry_dict.update(lang_text_map)
            writer.writerow(entry_dict)
