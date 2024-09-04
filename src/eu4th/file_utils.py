import csv
import logging
import pathlib
import re

from .models import LocalisationData, LocFile, LocLine

_LOC_LANG_RE = re.compile(r"^l_([a-z]+):$")
_LOC_SEPARATOR_RE = re.compile(r":[0-9]")


def _load_loc_from_file(
    filepath: pathlib.Path,
    language: str,
) -> LocFile | None:
    logging.info(f"Parsing locfile {str(filepath)!r}")
    lines = []
    with open(filepath, "r", encoding="utf-8-sig") as fh:
        # Get the language
        file_language_raw = fh.readline().strip()
        file_language_match = _LOC_LANG_RE.match(file_language_raw)
        if not file_language_match:
            logging.warning(f"Could not find language from file {filepath.name!r}")
            return None
        file_language = file_language_match.group(1)
        # Ignore unwanted languages
        if file_language != language:
            logging.info(f"Skipping {filepath.name!r}, wrong language ({file_language!r} instead of {language!r})")
            return None
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


def _merge_localisations(
    locfiles: list[LocFile],
    language: str,
) -> LocalisationData:
    logging.info("Merging localisations")
    locdata = LocalisationData(language=language)
    for locfile in locfiles:
        if locfile.language != locdata.language:
            continue
        for locline in locfile.lines:
            if locline.identifier in locdata.entries:
                logging.warning(f"Skipping duplicate definition of {locline.identifier!r}")
                continue
            locdata.entries[locline.identifier] = locline.text
    return locdata


def parse_localisation_from_locfiles(
    filepaths: list[pathlib.Path],
    language: str,
) -> LocalisationData:
    locfiles = []
    for filepath in filepaths:
        if not filepath.exists():
            continue
        locfile = _load_loc_from_file(filepath=filepath, language=language)
        if locfile is not None:
            locfiles.append(locfile)
    return _merge_localisations(locfiles=locfiles, language=language)


def parse_localisation_from_tsv(
    filepath: pathlib.Path,
    language: str,
) -> LocalisationData:
    logging.info(f"Parsing TSV {str(filepath)!r}")
    locdata = LocalisationData(language=language)
    with open(filepath, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(
            fh,
            delimiter="\t",
        )
        for entry in reader:
            identifier = entry["identifier"]
            text = entry.get(language)
            if text:
                locdata.entries[identifier] = text
    return locdata


def write_localisation_to_locfile(
    outfile: pathlib.Path,
    locdata: LocalisationData,
):
    logging.info(f"Writing localisation for language {locdata.language!r} to {str(outfile)!r}")
    with open(outfile, "w", encoding="utf-8") as fh:
        fh.write(f"l_{locdata.language}:\n")
        for identifier, text in locdata.entries.items():
            if text:
                text = text.replace('"', '\\"')
                fh.write(f' {identifier}:0 "{text}"\n')


def write_localisation_to_tsv(
    outpath: pathlib.Path,
    ref_locdata: LocalisationData,
    transl_locdata: LocalisationData,
):
    identifiers = sorted(set(ref_locdata.entries) | set(transl_locdata.entries))
    with open(outpath, "w", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "identifier",
                "status",
                ref_locdata.language,
                transl_locdata.language,
            ],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        for identifier in identifiers:
            entry_dict = {
                "identifier": identifier,
                "status": "",
                ref_locdata.language: ref_locdata.entries.get(identifier, ""),
                transl_locdata.language: transl_locdata.entries.get(identifier, ""),
            }
            writer.writerow(entry_dict)
