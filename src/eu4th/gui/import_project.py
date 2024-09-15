import logging
import pathlib
import tkinter as tk
import traceback
from tkinter import messagebox, ttk
from tkinter.filedialog import askdirectory

from ..project import add_known_project


class ImportProject(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__()
        self.title("Import existing project")
        self.report_callback_exception = self._handle_exception
        # Set the second column to grow
        self.columnconfigure(1, weight=1)

        # Create the input fields

        ttk.Label(self, text="Project directory").grid(row=0, column=0, sticky=tk.W)
        self.project_directory = tk.StringVar()
        project_directory_entry = ttk.Entry(self, width=60, textvariable=self.project_directory)
        project_directory_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        select_projdir_button = ttk.Button(
            self,
            text="Select...",
            command=self._select_project_directory,
        )
        select_projdir_button.grid(row=0, column=2, sticky=tk.W)

        # Add import button
        save_config_button = ttk.Button(self, text="Import", command=self._import_project)
        save_config_button.grid(row=2, column=1, sticky=tk.W)

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
        logging.debug("Opening directory selector")
        project_directory = askdirectory(mustexist=True)
        logging.debug(f"Selected directory: {project_directory}")
        self.project_directory.set(project_directory)

    def _import_project(self):
        if not self.project_directory.get():
            raise RuntimeError("Please enter a directory")
        add_known_project(project_directory=pathlib.Path(self.project_directory.get()))
        messagebox.showinfo(title="Done", message="Project imported")
        self.destroy()

    def _handle_exception(self, exc, val, tb):
        logging.exception(val)
        if isinstance(val, RuntimeError):
            message = str(val)
        else:
            message = traceback.format_exception(exc, val, tb)
        messagebox.showerror(title="Error", message=message)
