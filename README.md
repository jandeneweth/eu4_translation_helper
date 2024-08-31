# Translation helper tool

This tool allows you to easily translate localisation, by collecting all of it and providing it in an excel-compatible format.
When translation is done, you save the file again in the same format, 
and run the tool in 'flush' mode to generate translated localisation files.

## Requirements

Python 3.9 or higher. I developed and tested for 3.12, but normally 3.9 should work.
No additional libraries need to be installed!

## Usage

Steps:

3) Run the script to create the TSV: `python3 ./scripts/translation/eu4_translation_helper.py [...]`
2) Open the TSV file with Excel or similar applications. If it prompts to change the file format, reject!
3) Add translations. Add extra columns for languages if needed. The column name should match the language as used by EU4.
4) Save the file, making sure it saves to the same TSV file in the TSV format, not to a new excel-format file!
5) Run the script again in flush mode to create the new localisations in the localisation directory: `python3 ./scripts/translation/eu4_translation_helper.py [...] --flush`

If the translators don't have the prerequisites installed or too many issues pop up, someone else could generate the TSV file, 
share it for editing, and then 'flush' it back to localisation files.

Some notes:
- Only the translated languages are flushed to localisation files. Do not make changes in the reference language, those will be ignored.
- To avoid accidentally overwriting any translations you made and forgot to flush, the script will refuse to overwrite the TSV file if it already exists
