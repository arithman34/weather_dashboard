import tkinter as tk
from tkinter import messagebox

from frontend.constants import (
    BACKGROUND,
    FONT_BODY,
    FONT_LABEL,
    FONT_TITLE,
    MUTED,
    PRIMARY,
    TEXT,
)


class EditLocationDialog(tk.Toplevel):
    def __init__(self, master, token: str, location: dict, on_saved):
        super().__init__(master)
        self.title(f"Edit  —  {location['city']}, {location['country']}")
        self.resizable(False, False)
        self.grab_set()  # make modal — blocks interaction with parent window
        self.configure(bg=BACKGROUND)

        self._token = token
        self._location = location
        self._on_saved = on_saved

        self._build()
        self._center()

    def _build(self):
        wrapper = tk.Frame(self, bg=BACKGROUND, padx=32, pady=28)
        wrapper.pack()

        tk.Label(
            wrapper,
            text=f"{self._location['city']}, {self._location['country']}",
            font=FONT_TITLE,
            bg=BACKGROUND,
            fg=TEXT,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 4))

        tk.Label(wrapper, text="Alert Settings", font=FONT_BODY, bg=BACKGROUND, fg=MUTED).grid(
            row=1, column=0, columnspan=2, pady=(0, 20)
        )

        # Max threshold
        tk.Label(wrapper, text="Max temp (°C)", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(
            row=2, column=0, sticky="e", pady=8, padx=(0, 12)
        )
        self._max_entry = tk.Entry(wrapper, width=16, font=FONT_LABEL)
        self._max_entry.grid(row=2, column=1, sticky="w")
        if self._location.get("alert_threshold_max") is not None:
            self._max_entry.insert(0, str(self._location["alert_threshold_max"]))

        # Min threshold
        tk.Label(wrapper, text="Min temp (°C)", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(
            row=3, column=0, sticky="e", pady=8, padx=(0, 12)
        )
        self._min_entry = tk.Entry(wrapper, width=16, font=FONT_LABEL)
        self._min_entry.grid(row=3, column=1, sticky="w")
        if self._location.get("alert_threshold_min") is not None:
            self._min_entry.insert(0, str(self._location["alert_threshold_min"]))

        # Alert enabled toggle
        tk.Label(wrapper, text="Alerts enabled", font=FONT_LABEL, bg=BACKGROUND, fg=TEXT).grid(
            row=4, column=0, sticky="e", pady=8, padx=(0, 12)
        )
        self._alert_enabled = tk.BooleanVar(value=self._location.get("alert_enabled", False))
        tk.Checkbutton(
            wrapper,
            variable=self._alert_enabled,
            bg=BACKGROUND,
            activebackground=BACKGROUND,
            cursor="hand2",
        ).grid(row=4, column=1, sticky="w")

        # Buttons
        btn_frame = tk.Frame(wrapper, bg=BACKGROUND)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(24, 0))

        tk.Button(
            btn_frame,
            text="Save",
            font=FONT_LABEL,
            bg=PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            width=12,
            command=self._save,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame,
            text="Cancel",
            font=FONT_LABEL,
            bg=BACKGROUND,
            fg=TEXT,
            relief="flat",
            cursor="hand2",
            width=12,
            command=self.destroy,
        ).pack(side="left")

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        px = self.master.winfo_rootx()
        py = self.master.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _parse_float(self, entry: tk.Entry, field_name: str) -> float | None:
        value = entry.get().strip()
        if value == "":
            return None
        try:
            return float(value)
        except ValueError:
            messagebox.showerror("Invalid input", f"{field_name} must be a number.", parent=self)
            return "invalid"

    def _save(self):
        import threading

        from frontend.api import update_location

        max_val = self._parse_float(self._max_entry, "Max temp")
        if max_val == "invalid":
            return
        min_val = self._parse_float(self._min_entry, "Min temp")
        if min_val == "invalid":
            return

        def worker():
            try:
                updated = update_location(
                    self._token,
                    self._location["id"],
                    alert_threshold_max=max_val,
                    alert_threshold_min=min_val,
                    alert_enabled=self._alert_enabled.get(),
                )
                self.after(0, lambda: self._on_done(updated))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e), parent=self))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, updated: dict):
        self.destroy()
        self._on_saved(updated)
