import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

from frontend.components import make_card_row
from frontend.constants import (
    BACKGROUND,
    DANGER,
    FONT_BODY,
    FONT_HEADER,
    FONT_SECTION,
    MUTED,
    PRIMARY,
    TEXT,
)
from frontend.page import Page
from frontend.utils import ScrollableFrame

REFRESH_INTERVAL_MS = 60_000


class DashboardPage(Page):
    def __init__(self, master, stack, token: str):
        super().__init__(master, stack)
        self._token = token
        self._locations = []
        self._refresh_job = None

        self._build_header()
        self._build_toolbar()
        self._build_list()

        self.load_locations()
        self._schedule_refresh()

    def _schedule_refresh(self):
        self._refresh_job = self.after(REFRESH_INTERVAL_MS, self._auto_refresh)

    def _auto_refresh(self):
        self.load_locations()
        self._schedule_refresh()  # reschedule after each run

    def destroy(self):
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        super().destroy()

    def _build_header(self):
        header = tk.Frame(self, bg=BACKGROUND, padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="Weather Dashboard", font=FONT_HEADER, bg=BACKGROUND, fg=TEXT).pack(side="left")

        tk.Button(
            header,
            text="✕ Exit",
            bg=BACKGROUND,
            fg=DANGER,
            relief="flat",
            cursor="hand2",
            command=self.master.destroy,
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            header,
            text="Logout",
            bg=BACKGROUND,
            fg=DANGER,
            relief="flat",
            cursor="hand2",
            command=self._handle_logout,
        ).pack(side="right")

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BACKGROUND, padx=20, pady=4)
        bar.pack(fill="x")

        self._add_btn = tk.Button(
            bar,
            text="+ Add Location",
            bg=PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self._add_location,
        )
        self._add_btn.pack(side="left", padx=(0, 8))

        self._refresh_btn = tk.Button(
            bar,
            text="Refresh",
            bg=BACKGROUND,
            fg=TEXT,
            relief="flat",
            cursor="hand2",
            command=self.load_locations,
        )
        self._refresh_btn.pack(side="left")

        self._status_label = tk.Label(bar, text="", font=FONT_BODY, fg=MUTED, bg=BACKGROUND)
        self._status_label.pack(side="left", padx=12)

    def _build_list(self):
        tk.Label(self, text="Your Locations", font=FONT_SECTION, bg=BACKGROUND, fg=TEXT, padx=20).pack(
            anchor="w", pady=(8, 2)
        )

        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 12))

    def _run_in_thread(self, fn, *args, on_done=None, on_error=None, status=None):
        if status:
            self._status_label.config(text=status)
        self._set_buttons_enabled(False)

        def worker():
            try:
                result = fn(*args)
                self.after(0, lambda: self._on_thread_done(on_done, result))
            except Exception as e:
                self.after(0, lambda: self._on_thread_error(on_error, str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_thread_done(self, callback, result):
        self._status_label.config(text="")
        self._set_buttons_enabled(True)
        if callback:
            callback(result)

    def _on_thread_error(self, callback, error):
        self._status_label.config(text="")
        self._set_buttons_enabled(True)
        if callback:
            callback(error)

    def _set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self._add_btn.config(state=state)
        self._refresh_btn.config(state=state)

    def load_locations(self):
        from frontend.api import get_locations

        self._run_in_thread(
            get_locations,
            self._token,
            on_done=self._render_locations,
            on_error=lambda e: messagebox.showerror("Error", f"Failed to load locations: {e}"),
            status="Loading...",
        )

    def _render_locations(self, locations):
        self._locations = locations

        for widget in self._scrollable.interior.winfo_children():
            widget.destroy()

        if not self._locations:
            tk.Label(
                self._scrollable.interior,
                text="No locations yet. Click '+ Add Location' to get started.",
                font=FONT_BODY,
                fg=MUTED,
                bg=BACKGROUND,
                pady=20,
            ).pack()
            return

        make_card_row(
            self._scrollable.interior,
            self._locations,
            self._token,
            self.stack,
            on_fetch=self._fetch_weather,
            on_delete=self._delete_location,
            on_saved=lambda _: self.load_locations(),
        )

    def _handle_logout(self):
        self.stack.pop()

    def _fetch_weather(self, loc):
        from frontend.api import fetch_weather

        def on_done(_):
            messagebox.showinfo("Done", f"Weather updated for {loc['city']}. Refreshing...")
            self.load_locations()

        self._run_in_thread(
            fetch_weather,
            self._token,
            loc["id"],
            on_done=on_done,
            on_error=lambda e: messagebox.showerror("Error", str(e)),
            status=f"Fetching {loc['city']}...",
        )

    def _add_location(self):
        city = simpledialog.askstring("Add Location", "City name:")
        if not city:
            return

        country = simpledialog.askstring("Add Location", "Country code (e.g. GB, US):")
        if not country:
            return

        from frontend.api import create_location

        self._run_in_thread(
            create_location,
            self._token,
            city.strip(),
            country.strip().upper(),
            on_done=lambda _: self.load_locations(),
            on_error=lambda e: messagebox.showerror("Error", str(e)),
            status=f"Adding {city}...",
        )

    def _delete_location(self, loc):
        if not messagebox.askyesno("Confirm", f"Delete {loc['city']}, {loc['country']}?"):
            return

        from frontend.api import delete_location

        self._run_in_thread(
            delete_location,
            self._token,
            loc["id"],
            on_done=lambda _: self.load_locations(),
            on_error=lambda e: messagebox.showerror("Error", str(e)),
            status=f"Deleting {loc['city']}...",
        )
