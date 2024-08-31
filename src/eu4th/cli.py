import argparse
import logging
import pathlib
import sys

from .commands import flush_to_localisation, reload_localisation_to_tsv


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "A translation helper tool for Europa Universalis 4. "
            "Run in normal mode to (re-load) a localisations table, edit them (e.g. with Excel), "
            "and rerun the program in 'flush' mode to write the translations to a localisation file."
        ),
        epilog="Author: lichtkang",
    )
    parser.add_argument(
        "--reference_dir",
        type=str,
        required=True,
        help="Reference localisation files directory",
    )
    parser.add_argument(
        "--translation_filepath",
        type=str,
        required=True,
        help="Translation localisation file",
    )
    parser.add_argument(
        "--translation_language",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--reference_language",
        type=str,
        default="english",
    )
    parser.add_argument(
        "--exclude_reference",
        type=str,
        action="append",
        help="Regex patterns to ignore reference files",
    )
    parser.add_argument(
        "--flush",
        action="store_true",
        help="Flush translations to the translation file",
    )
    arguments = parser.parse_args()
    return arguments


def main():
    arguments = _parse_arguments()
    ref_dir = pathlib.Path(arguments.reference_dir).absolute()
    transl_fp = pathlib.Path(arguments.translation_filepath).absolute()
    translation_language = arguments.translation_language
    reference_language = arguments.translation_language
    reference_exclude_patterns = arguments.exclude_reference
    try:
        if arguments.flush:
            flush_to_localisation(
                transl_fp=transl_fp,
                translation_language=translation_language,
            )
        else:
            reload_localisation_to_tsv(
                ref_dir=ref_dir,
                transl_fp=transl_fp,
                reference_language=reference_language,
                translation_language=translation_language,
                reference_exclude_patterns=reference_exclude_patterns,
            )
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    logging.info("Done!")


if __name__ == "__main__":
    main()
