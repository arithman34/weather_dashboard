import tkinter as tk
from tkinter import messagebox

from frontend.constants import (
    BACKGROUND,
    FONT_BODY,
    FONT_HEADER,
    FONT_SECTION,
    MUTED,
    PRIMARY,
    TEXT,
)
from frontend.page import Page
from frontend.utils import ScrollableFrame


class WeatherHistoryPage(Page):
    def __init__(self, master, stack, token: str, location: dict):
        super().__init__(master, stack)
        self._token = token
        self._location = location

        self._build_header()
        self._build_list()
        self._load_history()

    def _build_header(self):
        header = tk.Frame(self, bg=BACKGROUND, padx=20, pady=12)
        header.pack(fill="x")

        tk.Button(
            header,
            text="← Back",
            font=FONT_BODY,
            bg=BACKGROUND,
            fg=PRIMARY,
            relief="flat",
            cursor="hand2",
            command=self.stack.pop,
        ).pack(side="left")

        tk.Label(
            header,
            text=f"Weather History  —  {self._location['city']}, {self._location['country']}",
            font=FONT_HEADER,
            bg=BACKGROUND,
            fg=TEXT,
        ).pack(side="left", padx=16)

    def _build_list(self):
        self._status_label = tk.Label(self, text="Loading...", font=FONT_BODY, fg=MUTED, bg=BACKGROUND)
        self._status_label.pack(anchor="w", padx=24, pady=(4, 0))

        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill="both", expand=True, padx=20, pady=(4, 12))

    def _load_history(self):
        import threading

        from frontend.api import get_weather_history

        def worker():
            try:
                records = get_weather_history(self._token, self._location["id"])
                self.after(0, lambda: self._render(records))
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _render(self, records: list):
        self._status_label.config(text=f"{len(records)} record(s) — most recent first")

        for widget in self._scrollable.interior.winfo_children():
            widget.destroy()

        if not records:
            tk.Label(
                self._scrollable.interior,
                text="No history available for this location yet.",
                font=FONT_BODY,
                fg=MUTED,
                bg=BACKGROUND,
                pady=20,
            ).pack()
            return

        for record in records:
            self._render_record_card(record)

    def _render_record_card(self, record: dict):
        from frontend.components import _format_recorded_at

        card = tk.Frame(
            self._scrollable.interior,
            bg="white",
            relief="groove",
            borderwidth=1,
            padx=16,
            pady=12,
        )
        card.pack(fill="x", padx=4, pady=3)

        # Timestamp header
        time_text = _format_recorded_at(record["recorded_at"])
        tk.Label(card, text=time_text, font=FONT_SECTION, bg="white", fg=TEXT, anchor="w").pack(fill="x")

        # Divider
        tk.Frame(card, bg="#e5e7eb", height=1).pack(fill="x", pady=(6, 8))

        # Weather details in a 2-column grid
        details = tk.Frame(card, bg="white")
        details.pack(fill="x")

        fields = [
            ("🌡  Temperature", f"{record['temperature']}°C"),
            ("🌡  Feels like", f"{record['feels_like']}°C" if record.get("feels_like") is not None else "—"),
            ("☁   Description", record.get("description") or "—"),
            ("💧  Humidity", f"{record['humidity']}%" if record.get("humidity") is not None else "—"),
            ("💨  Wind speed", f"{record['wind_speed']} km/h" if record.get("wind_speed") is not None else "—"),
        ]

        for row_idx, (label_text, value_text) in enumerate(fields):
            tk.Label(details, text=label_text, font=FONT_BODY, bg="white", fg=MUTED, anchor="w", width=20).grid(
                row=row_idx, column=0, sticky="w", pady=1
            )
            tk.Label(details, text=value_text, font=FONT_BODY, bg="white", fg=TEXT, anchor="w").grid(
                row=row_idx, column=1, sticky="w", pady=1, padx=(8, 0)
            )

    def _show_error(self, message: str):
        self._status_label.config(text="")
        messagebox.showerror("Error", f"Failed to load history: {message}")
        messagebox.showerror("Error", f"Failed to load history: {message}")
