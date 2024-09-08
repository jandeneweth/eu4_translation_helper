import os
import pathlib
import platform
import subprocess
import tkinter as tk


class PlaceholderEntry(tk.Entry):
    def __init__(
        self,
        master=None,
        *,
        placeholder="",
        fg="black",
        fg_placeholder="grey50",
        textvariable: tk.StringVar = None,
        **kwargs,
    ):
        super().__init__(master=master, bg="white", textvariable=textvariable, **kwargs)
        self._has_placeholder = True
        self.__textvariable = textvariable
        self.__textvariable.trace_add("write", callback=lambda x, y, z: self._set_placeholder_status(False))
        self.__textvariable.trace_add("unset", callback=lambda x, y, z: self._fill_placeholder())

        self.fg = fg
        self.fg_placeholder = fg_placeholder
        self.placeholder = placeholder
        self.bind("<FocusIn>", lambda event: self._clear_box())
        self.bind("<FocusOut>", lambda event: self._fill_placeholder())

        self._fill_placeholder()

    def set_placeholder(self, placeholder: str):
        self.placeholder = placeholder
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self._set_placeholder_status(True)  # Needed to maintain status

    def _clear_box(self):
        if not self.get() and super().get():
            self.delete(0, tk.END)
            self._set_placeholder_status(False)

    def _fill_placeholder(self):
        if not super().get():
            self.insert(0, self.placeholder)
            self._set_placeholder_status(True)

    def _set_placeholder_status(self, status: bool):
        if status is True:
            self.config(fg=self.fg_placeholder)
            self._has_placeholder = True
        else:
            self.config(fg=self.fg)
            self._has_placeholder = False


def open_with_filetype_default(target: pathlib.Path):
    # Based on https://www.reddit.com/r/Tkinter/comments/1d66073/comment/l6vfitz
    if not os.path.exists(target):
        raise RuntimeError(f"Target does not exist: {target!r}")
    try:
        if os.name in ["nt", "ce"]:
            # Windows
            # pylint: disable=no-member
            os.startfile(os.path.normpath(target))
        elif "darwin" in platform.system().casefold():
            # MacOS
            subprocess.run(["open", str(target)], check=True)
        else:
            # Assume linux
            subprocess.run(["xdg-open", str(target)], check=True)
    except Exception as e:
        raise RuntimeError(f"Could not open {target!r}: {e} ({type(e)})") from e
