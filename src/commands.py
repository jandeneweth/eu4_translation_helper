import pathlib
import re

from .file_utils import (
    parse_localisation_from_locfiles,
    parse_localisation_from_tsv,
    write_localisation_to_locfile,
    write_localisation_to_tsv,
)

_TSV_FILENAME = "translations.tsv"


def reload_localisation_to_tsv(
    tool_dir: pathlib.Path,
    ref_dir: pathlib.Path,
    transl_fp: pathlib.Path,
    reference_language: str,
    translation_language: str,
    reference_exclude_patterns: list[str],
):
    tsv_filepath = tool_dir / _TSV_FILENAME
    # TODO: Take existing TSV into account, extend it
    if tsv_filepath.exists():
        raise RuntimeError(
            f"The TSV file already exists, use the 'flush' flag to flush pending changes "
            f"to the localisation files first. Filepath: {str(tsv_filepath)!r}"
        )
    exclude_patterns_re = [re.compile(raw) for raw in reference_exclude_patterns]
    ref_files = [
        fp
        for fp in ref_dir.iterdir()
        if fp.is_file() and not any(pattern.match(str(fp)) for pattern in exclude_patterns_re)
    ]
    ref_locdata = parse_localisation_from_locfiles(
        filepaths=ref_files,
        language=reference_language,
    )
    transl_locdata = parse_localisation_from_locfiles(
        filepaths=[transl_fp],
        language=translation_language,
    )
    write_localisation_to_tsv(
        outpath=tsv_filepath,
        ref_locdata=ref_locdata,
        transl_locdata=transl_locdata,
    )


def flush_to_localisation(
    tool_dir: pathlib.Path,
    transl_fp: pathlib.Path,
    translation_language: str,
):
    tsv_filepath = tool_dir / _TSV_FILENAME
    locdata = parse_localisation_from_tsv(
        filepath=tsv_filepath,
        language=translation_language,
    )
    write_localisation_to_locfile(
        outfile=transl_fp,
        locdata=locdata,
    )
