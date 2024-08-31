# Translation helper tool

This tool allows you to easily translate localisations, by converting them to and from an excel-compatible format.

## Install

Make sure you installed Python (3.12 recommended). 
Optionally create a virtual environment to keep your system installation clean.

In the directory that contains the `pyproject.toml` file, run `python -m pip install .` to install this package.

## Usage

Steps:

1) Run the application with `python -m eu4th`. This will start a webserver and open the page in your browser. In case the page didn't load correctly, try a refresh.
2) Modify the configuration as required
3) Press the "load localisations" button
4) Open the TSV file with Excel or similar applications. If it prompts to change the file format, reject!
5) Add translations in the column of your language. The reference column is only there for viewing, changes to it do not persist.
6) Save the file, making sure it saves to the same TSV file in the TSV format, not to a new excel-format file!
7) Press the "flush translations" button
