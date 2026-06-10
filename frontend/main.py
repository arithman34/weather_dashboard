import tkinter as tk

from frontend.constants import BACKGROUND
from frontend.utils import PageStack
from frontend.views.login import LoginPage


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather Dashboard")
        self.configure(bg=BACKGROUND)
        self.attributes("-fullscreen", True)

        def _close(event):
            self.destroy()

        self.bind("<Escape>", lambda e: _close(e))

        self._stack = PageStack(self)
        self._stack.push(LoginPage)


if __name__ == "__main__":
    app = App()
    app.mainloop()
