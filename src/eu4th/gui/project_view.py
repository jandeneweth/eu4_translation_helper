import pathlib
import tkinter as tk
from tkinter import messagebox, ttk

from eu4th.commands import flush_to_localisation, reload_localisation_to_tsv
from eu4th.config_utils import Config, load_config, save_config
from eu4th.defines import EU4TH_DIR, EXCEL_FILEPATH
from eu4th.gui.gui_helpers import PlaceholderEntry, open_with_filetype_default


class ProjectView(ttk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        # Set the second column to grow
        self.columnconfigure(1, weight=1)

        # Create the input fields
        ttk.Label(self, text="Reference language").grid(column=0, row=0, sticky=tk.W)
        self.reference_language = tk.StringVar()
        reference_language_entry = ttk.Entry(self, width=60, textvariable=self.reference_language)
        reference_language_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Reference directory").grid(column=0, row=1, sticky=tk.W)
        self.reference_directory = tk.StringVar()
        reference_directory_entry = ttk.Entry(self, width=60, textvariable=self.reference_directory)
        reference_directory_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))
        open_reference_directory_button = ttk.Button(
            self,
            text="Open...",
            command=lambda: open_with_filetype_default(self.reference_directory.get()),
        )
        open_reference_directory_button.grid(column=2, row=1, sticky=tk.W)
        load_localisation_button = ttk.Button(self, text="Load localisations", command=self._load_localisation)
        load_localisation_button.grid(column=3, row=1, sticky=tk.W)

        ttk.Label(self, text="Translation table").grid(column=0, row=2, sticky=tk.W)
        self.translation_filepath = tk.StringVar()
        self.translation_filepath_entry = ttk.Label(self, text=EXCEL_FILEPATH)
        self.translation_filepath_entry.grid(column=1, row=2, sticky=(tk.W, tk.E))
        open_translations_button = ttk.Button(
            self,
            text="Open...",
            command=lambda: open_with_filetype_default(EXCEL_FILEPATH),
        )
        open_translations_button.grid(column=2, row=2, sticky=tk.W)

        ttk.Label(self, text="Translation language").grid(column=0, row=3, sticky=tk.W)
        self.translation_language = tk.StringVar()
        translation_language_entry = ttk.Entry(self, width=60, textvariable=self.translation_language)
        translation_language_entry.grid(column=1, row=3, sticky=(tk.W, tk.E))
        self.translation_language.trace_add("write", lambda x, y, z: self._update_translation_file_placeholder())

        ttk.Label(self, text="Translation output").grid(column=0, row=4, sticky=tk.W)
        self.translation_filepath = tk.StringVar()
        self.translation_filepath_entry = PlaceholderEntry(
            self, placeholder="translations_l_<language>.yml", width=60, textvariable=self.translation_filepath
        )
        self.translation_filepath_entry.grid(column=1, row=4, sticky=(tk.W, tk.E))
        open_translation_filepath_button = ttk.Button(
            self,
            text="Open...",
            command=lambda: open_with_filetype_default(self.translation_filepath.get()),
        )
        open_translation_filepath_button.grid(column=2, row=4, sticky=tk.W)
        flush_translations_button = ttk.Button(self, text="Flush translations", command=self._flush_translations)
        flush_translations_button.grid(column=3, row=4, sticky=tk.W)

        # Create the action buttons
        save_config_button = ttk.Button(self, text="Save configuration", command=self._save_config)
        save_config_button.grid(column=1, row=5, sticky=tk.W)

        # Add padding to all widgets
        for child in self.winfo_children():
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
            translation_language=self.config.translation_language,
            reference_exclude_patterns=self.config.exclude_references,
        )
        messagebox.showinfo(title="Results", message=feedback)

    def _flush_translations(self):
        feedback = flush_to_localisation(transl_fp=self.config.translation_filepath)
        messagebox.showinfo(title="Results", message=feedback)

    def _update_translation_file_placeholder(self):
        language = self.translation_language.get()
        self.translation_filepath_entry.set_placeholder(str(EU4TH_DIR / f"translations_l_{language}.yml"))
