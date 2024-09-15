import logging
import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from eu4th.gui.projects_overview import ProjectsOverview


class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EU4 Translation Helper")
        self.report_callback_exception = self._handle_exception
        self.minsize(width=400, height=260)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # Use frame for padding
        self._inner_frame = ttk.Frame(self, padding="3 3 12 12")
        self._inner_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self._inner_frame.columnconfigure(0, weight=1)
        self._inner_frame.rowconfigure(0, weight=1)
        # Add projects overview
        projects_overview = ProjectsOverview(parent=self._inner_frame, master=self)
        projects_overview.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    def _handle_exception(self, exc, val, tb):
        logging.exception(val)
        if isinstance(val, RuntimeError):
            message = str(val)
        else:
            message = traceback.format_exception(exc, val, tb)
        messagebox.showerror(title="Error", message=message)


def run(debug=False):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled")
    gui = Main()
    gui.mainloop()


if __name__ == "__main__":
    run(debug=True)
