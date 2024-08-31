import argparse
import logging
import pathlib
import sys

from .commands import flush_to_localisation, load_to_tsv


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert EU4's YAML localisation files to one TSV file for translation, or vice-versa. \n"
            "The TSV file can be edited in Excel or similar programs, but take care to save as TSV and not an excel-specific format! \n"
            "Without arguments, loads the localisation to a TSV file. Use the 'flush' flag to write back and backup the TSV (prefixed by 'previous_')."
            "Quirks specific for translation: \n"
            "    - Will not overwrite existing TSV files, use 'flush' to flush changes to the localisation files first. \n"
            "    - Only languages other than the reference language are written to localisation files. \n"
        ),
        epilog="Author: lichtkang",
    )
    parser.add_argument("--localisation_directory", type=str)
    parser.add_argument("--tsv_filepath", type=str)
    parser.add_argument("--reference_language", type=str)
    parser.add_argument("--exclude", type=str, action="append")
    parser.add_argument("--flush", action="store_true", help="Flush translations to localisation files")
    arguments = parser.parse_args()
    return arguments


def main():
    arguments = _parse_arguments()
    loc_dir = pathlib.Path(arguments.localisation_directory)
    tsv_filepath = pathlib.Path(arguments.tsv_filepath)
    reference_language = arguments.reference_language
    exclude_patterns = arguments.exclude
    try:
        if arguments.flush:
            flush_to_localisation(
                loc_dir=loc_dir,
                tsv_filepath=tsv_filepath,
                reference_language=reference_language,
            )
        else:
            load_to_tsv(
                loc_dir=loc_dir,
                tsv_filepath=tsv_filepath,
                reference_language=reference_language,
                exclude_patterns=exclude_patterns,
            )
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    logging.info("Done!")


if __name__ == "__main__":
    main()
