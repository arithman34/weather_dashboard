import tkinter as tk
from tkinter import messagebox

from frontend.constants import BACKGROUND, FONT_LABEL, FONT_TITLE, PRIMARY, TEXT
from frontend.page import Page


class RegisterPage(Page):
    def __init__(self, master, stack):
        super().__init__(master, stack)

        wrapper = tk.Frame(self, bg=BACKGROUND, padx=60, pady=60)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="Create Account", font=FONT_TITLE, bg=BACKGROUND, fg=TEXT).grid(
            row=0, column=0, columnspan=2, pady=(0, 24)
        )

        tk.Label(wrapper, text="Username", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(
            row=1, column=0, sticky="e", pady=6, padx=(0, 10)
        )
        self._username = tk.Entry(wrapper, width=28, font=FONT_LABEL)
        self._username.grid(row=1, column=1, pady=6)
        self._username.focus()

        tk.Label(wrapper, text="Email", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(row=2, column=0, sticky="e", pady=6, padx=(0, 10))
        self._email = tk.Entry(wrapper, width=28, font=FONT_LABEL)
        self._email.grid(row=2, column=1, pady=6)

        tk.Label(wrapper, text="Password", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(
            row=3, column=0, sticky="e", pady=6, padx=(0, 10)
        )
        self._password = tk.Entry(wrapper, show="*", width=28, font=FONT_LABEL)
        self._password.grid(row=3, column=1, pady=6)
        self._password.bind("<Return>", lambda _: self._handle_register())

        tk.Button(
            wrapper,
            text="Register",
            width=22,
            bg=PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._handle_register,
        ).grid(row=4, column=0, columnspan=2, pady=(20, 6))

        tk.Button(
            wrapper,
            text="Back to login",
            width=22,
            relief="flat",
            cursor="hand2",
            bg=BACKGROUND,
            fg=PRIMARY,
            command=self.stack.pop,
        ).grid(row=5, column=0, columnspan=2)

    def on_show(self):
        self._username.delete(0, tk.END)
        self._email.delete(0, tk.END)
        self._password.delete(0, tk.END)
        self._username.focus()

    def _handle_register(self):
        from frontend.api import register

        username = self._username.get().strip()
        email = self._email.get().strip()
        password = self._password.get().strip()

        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            register(username, email, password)
            messagebox.showinfo("Success", "Account created! Please log in.")
            self.stack.pop()
        except Exception as e:
            messagebox.showerror("Registration failed", str(e))
