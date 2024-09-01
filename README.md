# Translation helper tool

This tool allows you to easily translate localisations, by converting them to and from an excel-compatible format.

## Install

Download one of the releases from the github [releases page](https://github.com/jandeneweth/eu4_translation_helper/releases).

If no release is available for your system, you can either run it with python or build the executable. See below for instructions.

## Usage

1) Modify the configuration as required, use "Save configuration" to save it between sessions
2) Press the "load localisations" button
3) Open the TSV file with Excel or similar applications. If it prompts to change the file format, reject!
4) Add translations in the column of your language. The reference column is only there for viewing, changes to it do not persist.
5) Save the file, making sure it saves to the same TSV file in the TSV format, not to a new excel-format file!
6) Press the "flush translations" button

## Run from source

### Run with python

Install the right python version (see `pyproject.toml`), 
optionally create a virtual environment (recommended).
Install the package by running `python -m pip install .` in this directory.
Run the program with `python -m eu4th`.

### Build the executable

- Install the right python version and dependencies, including the build dependencies (see `pyproject.toml`), 
  optionally in a virtual environment (recommended).
- Build with pyinstaller: `pyinstaller eu4th_build.spec`
- Retrieve the executable from  `dist/eu4th.exe`