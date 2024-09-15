import logging
import pathlib
import tkinter as tk
from tkinter import messagebox, ttk

from ..project import load_known_projects, load_project, remove_known_project
from .create_project import CreateProject
from .import_project import ImportProject
from .project_view import ProjectView


class ProjectsOverview(ttk.Frame):
    def __init__(self, parent: tk.Widget, master: tk.Tk):
        super().__init__(parent)
        self.master = master

        # Create the projects listbox
        scrollbar = ttk.Scrollbar(self)
        self._listbox = ttk.Treeview(self, yscrollcommand=scrollbar.set, show="tree")
        scrollbar.configure(command=self._listbox.yview)
        self._listbox.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)

        # Add buttons in frame to the right of listbox
        self._button_frame = ttk.Frame(self, padding="3 3 12 12")
        self._button_frame.grid(row=0, column=1, sticky=(tk.N, tk.W))

        create_new_button = ttk.Button(
            self._button_frame,
            text="Create new...",
            command=self._create_new,
        )
        create_new_button.grid(
            row=0,
            column=0,
            sticky=(tk.N, tk.W),
            padx=6,
            pady=3,
        )
        import_existing_button = ttk.Button(
            self._button_frame,
            text="Find existing...",
            command=self._import_existing,
        )
        import_existing_button.grid(
            row=1,
            column=0,
            sticky=(tk.N, tk.W),
            padx=6,
            pady=3,
        )
        open_button = ttk.Button(
            self._button_frame,
            text="Open",
            command=self._open_project,
        )
        open_button.grid(
            row=2,
            column=0,
            sticky=(tk.N, tk.W),
            padx=6,
            pady=3,
        )
        open_button = ttk.Button(
            self._button_frame,
            text="Remove",
            command=self._remove_project,
        )
        open_button.grid(
            row=3,
            column=0,
            sticky=(tk.N, tk.W),
            padx=6,
            pady=3,
        )

        # Set initial state
        self._refresh_projects()

    def _refresh_projects(self):
        self._listbox.delete(*self._listbox.get_children())
        known_projects = load_known_projects()
        for project_directory in known_projects.project_directories:
            project = load_project(project_directory=project_directory)
            self._listbox.insert(
                parent="",
                index="end",
                id=project.project_directory,
                text=project.project_name,
            )

    def _create_new(self):
        CreateProject(master=self.master)
        self._refresh_projects()

    def _import_existing(self):
        ImportProject(master=self.master)
        self._refresh_projects()

    def _open_project(self):
        selected_item_id = self._listbox.focus()
        if not selected_item_id:
            raise RuntimeError("Please select a project from the list")
        logging.debug(f"Selected item id: {selected_item_id!r}")
        project = load_project(project_directory=pathlib.Path(selected_item_id))
        ProjectView(master=self.master, project=project)

    def _remove_project(self):
        selected_item_id = self._listbox.focus()
        if not selected_item_id:
            raise RuntimeError("Please select a project from the list")
        logging.debug(f"Selected item id: {selected_item_id!r}")
        remove_known_project(project_directory=pathlib.Path(selected_item_id))
        messagebox.showinfo(
            title="Done",
            message=(
                "Project removed from list. No files are removed in this process, those must be cleaned up manually."
            ),
        )
        self._refresh_projects()
