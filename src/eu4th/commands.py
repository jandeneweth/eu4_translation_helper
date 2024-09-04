import logging
import pathlib
import re

from .defines import EXCEL_FILEPATH
from .file_utils import (
    get_localisation_from_translations,
    merge_latest_references_into_translations,
    parse_localisation_from_locfiles,
    parse_translations_from_excel,
    write_localisation_to_locfile,
    write_translations_to_excel,
)
from .models import TranslationData


def reload_localisation_to_tsv(
    ref_dir: pathlib.Path,
    reference_language: str,
    translation_language: str,
    reference_exclude_patterns: list[str],
):
    # Get reference localisations
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
    # Get translaton data
    if EXCEL_FILEPATH.exists():
        translation_data = parse_translations_from_excel(filepath=EXCEL_FILEPATH)
        if translation_data.reference_language != reference_language:
            raise RuntimeError(
                f"Reference language does not match: {reference_language!r} "
                f"versus {translation_data.reference_language!r} in existing data"
            )
        if translation_data.translation_language != translation_language:
            raise RuntimeError(
                f"Translation language does not match: {translation_language!r} "
                f"versus {translation_data.translation_language!r} in existing data"
            )
    else:
        translation_data = TranslationData(
            reference_language=reference_language,
            translation_language=translation_language,
        )
    # Update translation data with references
    translation_data, stats = merge_latest_references_into_translations(
        known_translations=translation_data,
        latest_locdata=ref_locdata,
    )
    # Update TSV file
    write_translations_to_excel(
        outpath=EXCEL_FILEPATH,
        translation_data=translation_data,
    )
    info = f"Loaded {len(ref_locdata.entries)} references: "
    if stats.all > 0:
        info += (
            f"{stats.new} new, {stats.changed} changed, {stats.deleted} deleted "
            f"- {stats.outdated_translations} translations became outdated"
        )
    else:
        info += "no changes"
    logging.info(info)
    return info


def flush_to_localisation(transl_fp: pathlib.Path):
    if not EXCEL_FILEPATH.exists():
        raise RuntimeError(
            f"The translation table does not yet exist, load localisation first (path {str(EXCEL_FILEPATH)!r})"
        )
    translation_data = parse_translations_from_excel(filepath=EXCEL_FILEPATH)
    locdata = get_localisation_from_translations(translation_data=translation_data)
    written = write_localisation_to_locfile(
        outfile=transl_fp,
        locdata=locdata,
    )
    info = f"Flushed {written} translations"
    logging.info(info)
    return info
