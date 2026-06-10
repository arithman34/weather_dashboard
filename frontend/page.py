import tkinter as tk

from frontend.constants import BACKGROUND
from frontend.utils import PageStack


class Page(tk.Frame):
    def __init__(self, master, stack: PageStack):
        super().__init__(master, bg=BACKGROUND)
        self.stack = stack

    def on_show(self) -> None:
        pass
