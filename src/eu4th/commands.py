import logging
import pathlib
import re

from .defines import TSV_FILEPATH
from .file_utils import (
    parse_localisation_from_locfiles,
    parse_localisation_from_tsv,
    write_localisation_to_locfile,
    write_localisation_to_tsv,
)


def reload_localisation_to_tsv(
    ref_dir: pathlib.Path,
    transl_fp: pathlib.Path,
    reference_language: str,
    translation_language: str,
    reference_exclude_patterns: list[str],
):
    exclude_patterns_re = [re.compile(raw) for raw in reference_exclude_patterns]
    ref_files = [
        fp
        for fp in ref_dir.rglob("*")
        if fp.is_file()
        and fp.name.endswith(".yml")
        and not any(pattern.match(str(fp)) for pattern in exclude_patterns_re)
    ]
    ref_locdata = parse_localisation_from_locfiles(
        filepaths=ref_files,
        language=reference_language,
    )
    transl_locdata = parse_localisation_from_locfiles(
        filepaths=[transl_fp],
        language=translation_language,
    )
    if TSV_FILEPATH.exists():
        # If TSV file already exists, prefer its data
        tsv_transl_locdata = parse_localisation_from_tsv(
            filepath=TSV_FILEPATH,
            language=translation_language,
        )
        transl_locdata.entries.update(tsv_transl_locdata.entries)
    write_localisation_to_tsv(
        outpath=TSV_FILEPATH,
        ref_locdata=ref_locdata,
        transl_locdata=transl_locdata,
    )
    info = f"Loaded {len(ref_locdata.entries)} references and {len(transl_locdata.entries)} existing translation"
    logging.info(info)
    return info


def flush_to_localisation(
    transl_fp: pathlib.Path,
    translation_language: str,
):
    if not TSV_FILEPATH.exists():
        raise RuntimeError(f"The TSV file does not yet exist, load localisation first (path {str(TSV_FILEPATH)!r})")
    locdata = parse_localisation_from_tsv(
        filepath=TSV_FILEPATH,
        language=translation_language,
    )
    write_localisation_to_locfile(
        outfile=transl_fp,
        locdata=locdata,
    )
    info = f"Flushed {len(locdata.entries)} translations"
    logging.info(info)
    return info
