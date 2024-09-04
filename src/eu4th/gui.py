import logging
import pathlib
import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from eu4th.commands import flush_to_localisation, reload_localisation_to_tsv
from eu4th.config_utils import Config, load_config, save_config
from eu4th.defines import TSV_FILEPATH
from eu4th.gui_helpers import PlaceholderEntry, open_with_filetype_default


class Gui:
    def __init__(self, root: tk.Tk):
        # Set error handler
        root.report_callback_exception = self._handle_exception

        # Set title
        root.title("EU4 Translation Helper")

        # Create the frame and configure the grid
        root.minsize(width=400, height=260)
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=1)

        # Create the input fields
        ttk.Label(mainframe, text="Reference language").grid(column=0, row=0, sticky=tk.W)
        self.reference_language = tk.StringVar()
        reference_language_entry = ttk.Entry(mainframe, width=60, textvariable=self.reference_language)
        reference_language_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))

        ttk.Label(mainframe, text="Reference directory").grid(column=0, row=1, sticky=tk.W)
        self.reference_directory = tk.StringVar()
        reference_directory_entry = ttk.Entry(mainframe, width=60, textvariable=self.reference_directory)
        reference_directory_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))

        ttk.Label(mainframe, text="Translation language").grid(column=0, row=2, sticky=tk.W)
        self.translation_language = tk.StringVar()
        translation_language_entry = ttk.Entry(mainframe, width=60, textvariable=self.translation_language)
        translation_language_entry.grid(column=1, row=2, sticky=(tk.W, tk.E))
        self.translation_language.trace_add("write", lambda x, y, z: self._update_translation_file_placeholder())

        ttk.Label(mainframe, text="Translation output").grid(column=0, row=3, sticky=tk.W)
        self.translation_filepath = tk.StringVar()
        self.translation_filepath_entry = PlaceholderEntry(
            mainframe, placeholder="translations_l_<language>.yml", width=60, textvariable=self.translation_filepath
        )
        self.translation_filepath_entry.grid(column=1, row=3, sticky=(tk.W, tk.E))

        # Create the action buttons
        load_localisation_button = ttk.Button(mainframe, text="Save configuration", command=self._save_config)
        load_localisation_button.grid(column=1, row=4, sticky=tk.W)
        load_localisation_button = ttk.Button(mainframe, text="Load localisations", command=self._load_localisation)
        load_localisation_button.grid(column=1, row=5, sticky=tk.W)
        load_localisation_button = ttk.Button(mainframe, text="Open translations", command=self._open_translations)
        load_localisation_button.grid(column=1, row=6, sticky=tk.W)
        flush_translations_button = ttk.Button(mainframe, text="Flush translations", command=self._flush_translations)
        flush_translations_button.grid(column=1, row=7, sticky=tk.W)

        # Add padding to all widgets
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Focus on the 'flush' button
        flush_translations_button.focus()

        # Load config from settings
        self.config = load_config()

    @property
    def config(self) -> Config:
        return Config(
            reference_directory=pathlib.Path(self.reference_directory.get()),
            reference_language=self.reference_language.get(),
            translation_filepath=pathlib.Path(self.translation_filepath.get()),
            translation_language=self.translation_language.get(),
        )

    @config.setter
    def config(self, config: Config) -> None:
        self.reference_directory.set(config.reference_directory)
        self.reference_language.set(config.reference_language)
        self.translation_filepath.set(config.translation_filepath)
        self.translation_language.set(config.translation_language)

    def _save_config(self):
        save_config(config=self.config)
        messagebox.showinfo(title="Results", message="Configuration saved")
        self.config = load_config()

    def _load_localisation(self):
        feedback = reload_localisation_to_tsv(
            ref_dir=self.config.reference_directory,
            reference_language=self.config.reference_language,
            transl_fp=self.config.translation_filepath,
            translation_language=self.config.translation_language,
            reference_exclude_patterns=self.config.exclude_references,
        )
        messagebox.showinfo(title="Results", message=feedback)

    def _open_translations(self):
        open_with_filetype_default(TSV_FILEPATH)

    def _flush_translations(self):
        feedback = flush_to_localisation(
            transl_fp=self.config.translation_filepath,
            translation_language=self.config.translation_language,
        )
        messagebox.showinfo(title="Results", message=feedback)

    def _handle_exception(self, exc, val, tb):
        logging.exception(exc)
        if isinstance(exc, RuntimeError):
            message = str(exc)
        else:
            message = traceback.format_exception(exc, val, tb)
        messagebox.showerror(title="Error", message=message)

    def _update_translation_file_placeholder(self):
        language = self.translation_language.get()
        self.translation_filepath_entry.set_placeholder(f"translations_l_{language}.yml")


def run():
    root = tk.Tk()
    Gui(root=root)
    root.mainloop()


if __name__ == "__main__":
    run()
