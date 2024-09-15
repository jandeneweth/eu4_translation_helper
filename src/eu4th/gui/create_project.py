import logging
import pathlib
import tkinter as tk
import traceback
from tkinter import messagebox, ttk
from tkinter.filedialog import askdirectory

from ..commands import reload_localisation_to_tsv
from ..project import Project, add_known_project, save_project
from .gui_helpers import PlaceholderEntry


class CreateProject(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__()
        self.title("Create project")
        self.report_callback_exception = self._handle_exception

        # Set the second column to grow
        self.columnconfigure(1, weight=1)

        # Create the input fields

        ttk.Label(self, text="Project name").grid(row=0, column=0, sticky=tk.W)
        self.project_name = tk.StringVar()
        project_name_entry = ttk.Entry(self, width=60, textvariable=self.project_name)
        project_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Project directory").grid(row=1, column=0, sticky=tk.W)
        self.project_directory = tk.StringVar()
        project_directory_entry = ttk.Entry(self, width=60, textvariable=self.project_directory)
        project_directory_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        select_projdir_button = ttk.Button(
            self,
            text="Select...",
            command=self._select_project_directory,
        )
        select_projdir_button.grid(row=1, column=2, sticky=tk.W)

        ttk.Label(self, text="Reference language").grid(row=2, column=0, sticky=tk.W)
        self.reference_language = tk.StringVar()
        reference_language_entry = PlaceholderEntry(
            self, placeholder="english", width=60, textvariable=self.reference_language
        )
        reference_language_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Reference text directory").grid(row=3, column=0, sticky=tk.W)
        self.reference_directory = tk.StringVar()
        reference_directory_entry = ttk.Entry(self, width=60, textvariable=self.reference_directory)
        reference_directory_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))
        select_refdir_button = ttk.Button(
            self,
            text="Select...",
            command=self._select_reference_directory,
        )
        select_refdir_button.grid(row=3, column=2, sticky=tk.W)

        ttk.Label(self, text="Translation language").grid(row=4, column=0, sticky=tk.W)
        self.translation_language = tk.StringVar()
        translation_language_entry = ttk.Entry(self, width=60, textvariable=self.translation_language)
        translation_language_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

        ttk.Label(self, text="Existing translations directory (optional)").grid(row=5, column=0, sticky=tk.W)
        self.existing_translations = tk.StringVar()
        existing_translations_entry = ttk.Entry(self, width=60, textvariable=self.existing_translations)
        existing_translations_entry.grid(row=5, column=1, sticky=(tk.W, tk.E))
        select_exist_tr_dir_button = ttk.Button(
            self,
            text="Select...",
            command=self._select_existing_translations,
        )
        select_exist_tr_dir_button.grid(row=5, column=2, sticky=tk.W)

        # Add save button
        save_config_button = ttk.Button(self, text="Finish", command=self._create_project)
        save_config_button.grid(row=6, column=1, sticky=tk.W)

        # Add padding to all widgets
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Focus on the 'project_directory' input
        project_directory_entry.focus()

        # Block master window until this one is done
        self.transient(master)
        self.grab_set()
        master.wait_window(self)

    def _select_project_directory(self):
        project_directory = askdirectory(mustexist=True)
        self.project_directory.set(project_directory)

    def _select_reference_directory(self):
        reference_directory = askdirectory(mustexist=True)
        self.reference_directory.set(reference_directory)

    def _select_existing_translations(self):
        existing_translations = askdirectory(mustexist=True)
        self.existing_translations.set(existing_translations)

    def _create_project(self):
        if not self.project_directory.get():
            raise RuntimeError("Missing project name")
        if not self.project_directory.get():
            raise RuntimeError("Missing project directory")
        if not self.reference_directory.get():
            raise RuntimeError("Missing reference text directory")
        if not self.reference_language.get():
            raise RuntimeError("Missing reference language")
        if not self.translation_language.get():
            raise RuntimeError("Missing translation language")
        existing_translations_dir = (
            pathlib.Path(self.existing_translations.get()) if self.existing_translations.get() else None
        )
        translations_outfile = None
        if existing_translations_dir:
            translations_outfile = (
                existing_translations_dir / f"all_translations_l_{self.translation_language.get()}.yml"
            )
        project = Project(
            project_name=self.project_name.get(),
            project_directory=pathlib.Path(self.project_directory.get()).resolve(),
            reference_directory=pathlib.Path(self.reference_directory.get()).resolve(),
            reference_language=self.reference_language.get(),
            translation_language=self.translation_language.get(),
            translation_outfile=translations_outfile,
        )
        save_project(project=project)
        add_known_project(project_directory=project.project_directory)
        try:
            reload_localisation_to_tsv(
                ref_dir=project.reference_directory,
                reference_language=project.reference_language,
                translation_language=project.translation_language,
                reference_exclude_patterns=project.exclude_references,
                translation_table=project.translations_table,
                existing_translations_dir=existing_translations_dir,
            )
        finally:
            messagebox.showinfo(title="Done", message="Project created and data imported")
            self.destroy()

    def _handle_exception(self, exc, val, tb):
        logging.exception(val)
        if isinstance(val, RuntimeError):
            message = str(val)
        else:
            message = traceback.format_exception(exc, val, tb)
        messagebox.showerror(title="Error", message=message)
