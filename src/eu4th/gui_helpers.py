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
