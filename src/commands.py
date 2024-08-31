import pathlib

from .file_utils import (
    parse_localisation_from_locfiles,
    parse_localisation_from_tsv,
    write_localisation_to_locfiles,
    write_localisation_to_tsv,
)


def load_to_tsv(
    loc_dir: pathlib.Path,
    tsv_filepath: pathlib.Path,
    reference_language: str,
    exclude_patterns: list[str],
):
    """Load localisation to TSV file"""
    if tsv_filepath.exists():
        raise RuntimeError(
            f"The TSV file already exists, use the 'flush' flag to flush pending changes "
            f"to the localisation files first. Filepath: {str(tsv_filepath)!r}"
        )
    locdata = parse_localisation_from_locfiles(dirpath=loc_dir, exclude_patterns=exclude_patterns)
    write_localisation_to_tsv(outpath=tsv_filepath, locdata=locdata, reference_language=reference_language)


def flush_to_localisation(
    loc_dir: pathlib.Path,
    tsv_filepath: pathlib.Path,
    reference_language: str,
):
    """Write TSV file to localisation and rename it"""
    locdata = parse_localisation_from_tsv(filepath=tsv_filepath)
    write_localisation_to_locfiles(
        loc_dir=loc_dir,
        locdata=locdata,
        reference_language=reference_language,
    )
    backup_tsv_filepath = tsv_filepath.parent / f"previous_{tsv_filepath.name}"
    tsv_filepath.replace(backup_tsv_filepath)
