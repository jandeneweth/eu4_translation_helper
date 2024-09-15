import logging
import pathlib
import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from eu4th.commands import flush_to_localisation, reload_localisation_to_tsv
from eu4th.gui.gui_helpers import open_with_filetype_default

from ..project import Project, save_project


class ProjectView(tk.Toplevel):
    def __init__(self, master: tk.Tk, project: Project):
        super().__init__()
        self.title(f"Project - {project.project_name}")
        self.report_callback_exception = self._handle_exception
        self.project = project

        # Set the second column to grow
        self.columnconfigure(1, weight=1)

        # Create the input fields
        ttk.Label(self, text="Reference language").grid(column=0, row=0, sticky=tk.W)
        reference_language_entry = ttk.Label(self, width=60, text=self.project.reference_language)
        reference_language_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Reference directory").grid(column=0, row=1, sticky=tk.W)
        self.reference_directory = tk.StringVar(value=str(project.reference_directory))
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
        translations_table_entry = ttk.Label(self, text=str(self.project.translations_table))
        translations_table_entry.grid(column=1, row=2, sticky=(tk.W, tk.E))
        open_translations_button = ttk.Button(
            self,
            text="Open...",
            command=lambda: open_with_filetype_default(self.project.translations_table),
        )
        open_translations_button.grid(column=2, row=2, sticky=tk.W)

        ttk.Label(self, text="Translation language").grid(column=0, row=3, sticky=tk.W)
        translation_language_entry = ttk.Label(self, width=60, text=self.project.translation_language)
        translation_language_entry.grid(column=1, row=3, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Translation output").grid(column=0, row=4, sticky=tk.W)
        self.translation_outfile = tk.StringVar(
            value=str(project.translation_outfile) if project.translation_outfile else ""
        )
        self.translation_outfile_entry = ttk.Entry(self, width=60, textvariable=self.translation_outfile)
        self.translation_outfile_entry.grid(column=1, row=4, sticky=(tk.W, tk.E))
        open_translation_outfile_button = ttk.Button(
            self,
            text="Open...",
            command=lambda: open_with_filetype_default(self.translation_outfile.get()),
        )
        open_translation_outfile_button.grid(column=2, row=4, sticky=tk.W)
        flush_translations_button = ttk.Button(self, text="Flush translations", command=self._flush_translations)
        flush_translations_button.grid(column=3, row=4, sticky=tk.W)

        # Add the update config button
        update_config_button = ttk.Button(self, text="Save configuration changes", command=self._update_config)
        update_config_button.grid(column=1, row=5, sticky=tk.W)

        # Add padding to all widgets
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Focus on the 'flush' button
        flush_translations_button.focus()

        # Block master window until this one is done
        self.transient(master)
        self.grab_set()
        master.wait_window(self)

    def _update_config(self):
        self.project.reference_directory = pathlib.Path(self.reference_directory.get())
        self.project.translation_outfile = pathlib.Path(self.translation_outfile.get())
        save_project(project=self.project)
        messagebox.showinfo(title="Done", message="Configuration saved")

    def _load_localisation(self):
        feedback = reload_localisation_to_tsv(
            ref_dir=pathlib.Path(self.reference_directory.get()),
            reference_language=self.project.reference_language,
            translation_language=self.project.translation_language,
            reference_exclude_patterns=self.project.exclude_references,
            translation_table=self.project.translations_table,
        )
        messagebox.showinfo(title="Results", message=feedback)

    def _flush_translations(self):
        if not self.translation_outfile.get():
            raise RuntimeError("Select a translations output file first")
        feedback = flush_to_localisation(
            translation_table=self.project.translations_table,
            translation_outfile=pathlib.Path(self.translation_outfile.get()),
        )
        messagebox.showinfo(title="Results", message=feedback)

    def _handle_exception(self, exc, val, tb):
        logging.exception(val)
        if isinstance(val, RuntimeError):
            message = str(val)
        else:
            message = traceback.format_exception(exc, val, tb)
        messagebox.showerror(title="Error", message=message)
