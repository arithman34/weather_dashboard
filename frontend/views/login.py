import tkinter as tk
from tkinter import messagebox

from frontend.constants import BACKGROUND, FONT_LABEL, FONT_TITLE, PRIMARY, TEXT
from frontend.page import Page


class LoginPage(Page):
    def __init__(self, master, stack):
        super().__init__(master, stack)

        wrapper = tk.Frame(self, bg=BACKGROUND, padx=60, pady=60)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="Weather Dashboard", font=FONT_TITLE, bg=BACKGROUND, fg=TEXT).grid(
            row=0, column=0, columnspan=2, pady=(0, 24)
        )

        tk.Label(wrapper, text="Username", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(row=1, column=0, sticky="e", pady=6, padx=(0, 10))
        self._username = tk.Entry(wrapper, width=28, font=FONT_LABEL)
        self._username.grid(row=1, column=1, pady=6)
        self._username.focus()

        tk.Label(wrapper, text="Password", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(row=2, column=0, sticky="e", pady=6, padx=(0, 10))
        self._password = tk.Entry(wrapper, show="*", width=28, font=FONT_LABEL)
        self._password.grid(row=2, column=1, pady=6)
        self._password.bind("<Return>", lambda _: self._handle_login())

        tk.Button(
            wrapper, text="Login", width=22, bg=PRIMARY, fg="white",
            relief="flat", cursor="hand2", command=self._handle_login,
        ).grid(row=3, column=0, columnspan=2, pady=(20, 6))

        tk.Button(
            wrapper, text="Create an account", width=22,
            relief="flat", cursor="hand2", bg=BACKGROUND, fg=PRIMARY,
            command=self._go_register,
        ).grid(row=4, column=0, columnspan=2)

    def on_show(self):
        self._username.delete(0, tk.END)
        self._password.delete(0, tk.END)
        self._username.focus()

    def _handle_login(self):
        from frontend.api import login
        from frontend.views.dashboard import DashboardPage

        username = self._username.get().strip()
        password = self._password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            token = login(username, password)
            self.stack.push(DashboardPage, token=token)
        except Exception as e:
            messagebox.showerror("Login failed", str(e))

    def _go_register(self):
        from frontend.views.register import RegisterPage
        self.stack.push(RegisterPage)
