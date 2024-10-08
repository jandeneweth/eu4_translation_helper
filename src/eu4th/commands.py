import logging
import pathlib
import re

from .file_utils import (
    get_localisation_from_translations,
    merge_latest_references_into_translations,
    parse_localisation_from_locfiles,
    parse_translations_from_excel,
    write_localisation_to_locfile,
    write_translations_to_excel,
)
from .models import TranslationData, TranslationEntry, TranslationStatus


def reload_localisation_to_tsv(
    ref_dir: pathlib.Path,
    reference_language: str,
    translation_language: str,
    reference_exclude_patterns: list[str],
    translation_table: pathlib.Path,
    existing_translations_dir: pathlib.Path | None = None,
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
    # Get translation data
    if existing_translations_dir is not None:
        if not existing_translations_dir.is_dir():
            raise RuntimeError(f"Not a valid directory for existing translations: {str(existing_translations_dir)!r}")
        logging.debug(f"Loading translations from existing directory: {str(existing_translations_dir)!r}")
        transl_files = [fp for fp in existing_translations_dir.rglob("*") if fp.is_file() and fp.name.endswith(".yml")]
        existing_translations_locdata = parse_localisation_from_locfiles(
            filepaths=transl_files,
            language=translation_language,
        )
        translation_data = TranslationData(
            reference_language=reference_language,
            translation_language=translation_language,
            entries={
                ref_id: TranslationEntry(
                    reference=ref_text,
                    translation=existing_translations_locdata.entries.get(ref_id),
                    status=TranslationStatus.MISSING,
                )
                for ref_id, ref_text in ref_locdata.entries.items()
            },
        )
    elif translation_table.exists():
        logging.debug(f"Loading translations from existing table: {str(translation_table)!r}")
        translation_data = parse_translations_from_excel(filepath=translation_table)
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
        logging.debug("No existing translations to start from")
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
        outpath=translation_table,
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


def flush_to_localisation(
    translation_table: pathlib.Path,
    translation_outfile: pathlib.Path,
):
    if not translation_table.exists():
        raise RuntimeError(
            f"The translation table does not yet exist, load localisation first (path {str(translation_table)!r})"
        )
    if not translation_outfile.parent.exists():
        raise RuntimeError(f"Parent directory of output file must exist: {str(translation_outfile.parent)!r}")
    translation_data = parse_translations_from_excel(filepath=translation_table)
    locdata = get_localisation_from_translations(translation_data=translation_data)
    written = write_localisation_to_locfile(
        outfile=translation_outfile,
        locdata=locdata,
    )
    info = f"Flushed {written} translations"
    logging.info(info)
    return info
