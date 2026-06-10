import threading
import tkinter as tk
from collections.abc import Callable
from datetime import datetime, timezone

from frontend.constants import (
    BACKGROUND,
    DANGER,
    FONT_BODY,
    FONT_SECTION,
    MUTED,
    PRIMARY,
    TEXT,
)

CARD_BG = "white"
CARD_RELIEF = "groove"
CARD_PADDING = 14


CARDS_PER_ROW = 3


def make_card_row(
    parent: tk.Frame,
    locations: list,
    token: str,
    stack,
    on_fetch: Callable,
    on_delete: Callable,
    on_saved: Callable,
) -> None:
    chunks = [locations[i : i + CARDS_PER_ROW] for i in range(0, len(locations), CARDS_PER_ROW)]

    for chunk in chunks:
        row_frame = tk.Frame(parent, bg=BACKGROUND)
        row_frame.pack(fill="x", padx=8, pady=8)

        # Always configure all columns so every card is the same width
        for col in range(CARDS_PER_ROW):
            row_frame.columnconfigure(col, weight=1, uniform="card")

        for col, loc in enumerate(chunk):
            card = _make_card(row_frame, loc, token, stack, on_fetch, on_delete, on_saved)
            card.grid(row=0, column=col, sticky="nsew", padx=6)


def _make_card(
    parent: tk.Frame,
    loc: dict,
    token: str,
    stack,
    on_fetch: Callable,
    on_delete: Callable,
    on_saved: Callable,
) -> tk.Frame:
    card = tk.Frame(parent, bg=CARD_BG, relief=CARD_RELIEF, borderwidth=1, padx=CARD_PADDING, pady=CARD_PADDING)

    # City / country heading
    tk.Label(
        card,
        text=f"{loc['city']}, {loc['country']}",
        font=FONT_SECTION,
        bg=CARD_BG,
        fg=TEXT,
        anchor="w",
    ).pack(fill="x")

    # Divider
    tk.Frame(card, bg="#e5e7eb", height=1).pack(fill="x", pady=(6, 8))

    # Weather data — updated by background thread once loaded
    weather_label = tk.Label(card, text="Loading...", font=FONT_BODY, fg=MUTED, bg=CARD_BG, anchor="w", justify="left")
    weather_label.pack(fill="x")

    # Timestamp
    time_label = tk.Label(card, text="", font=FONT_BODY, fg=MUTED, bg=CARD_BG, anchor="w")
    time_label.pack(fill="x", pady=(6, 0))

    # Buttons — left side: Fetch, History | right side: Edit, Delete
    btn_frame = tk.Frame(card, bg=CARD_BG)
    btn_frame.pack(fill="x", pady=(10, 0))

    tk.Button(
        btn_frame,
        text="Fetch",
        font=FONT_BODY,
        fg=PRIMARY,
        bg=CARD_BG,
        relief="flat",
        cursor="hand2",
        command=lambda: on_fetch(loc),
    ).pack(side="left")

    tk.Button(
        btn_frame,
        text="History",
        font=FONT_BODY,
        fg=PRIMARY,
        bg=CARD_BG,
        relief="flat",
        cursor="hand2",
        command=lambda: _open_history(stack, token, loc),
    ).pack(side="left", padx=(4, 0))

    tk.Button(
        btn_frame,
        text="Delete",
        font=FONT_BODY,
        fg=DANGER,
        bg=CARD_BG,
        relief="flat",
        cursor="hand2",
        command=lambda: on_delete(loc),
    ).pack(side="right")

    tk.Button(
        btn_frame,
        text="Edit",
        font=FONT_BODY,
        fg=TEXT,
        bg=CARD_BG,
        relief="flat",
        cursor="hand2",
        command=lambda: _open_edit(card, token, loc, on_saved),
    ).pack(side="right", padx=(0, 4))

    _load_weather(card, weather_label, time_label, loc, token)

    return card


def _open_history(stack, token: str, loc: dict) -> None:
    from frontend.views.weather_history import WeatherHistoryPage

    stack.push(WeatherHistoryPage, token=token, location=loc)


def _open_edit(parent: tk.Frame, token: str, loc: dict, on_saved: Callable) -> None:
    from frontend.views.edit_location import EditLocationDialog

    EditLocationDialog(parent, token=token, location=loc, on_saved=on_saved)


def _load_weather(card: tk.Frame, label: tk.Label, time_label: tk.Label, loc: dict, token: str) -> None:
    from frontend.api import get_latest_weather

    def worker():
        try:
            weather = get_latest_weather(token, loc["id"])
            text = (
                f"🌡  {weather['temperature']}°C  (feels {weather['feels_like']}°C)\n"
                f"☁  {weather['description']}\n"
                f"💧 {weather['humidity']}%  humidity\n"
                f"💨 {weather['wind_speed']} km/h  wind"
            )
            time_text = _format_recorded_at(weather["recorded_at"])
            card.after(0, lambda: _safe_update(label, text, TEXT))
            card.after(0, lambda: _safe_update(time_label, time_text, MUTED))
        except Exception:
            card.after(0, lambda: _safe_update(label, "No data yet", MUTED))
            card.after(0, lambda: _safe_update(time_label, "", MUTED))

    threading.Thread(target=worker, daemon=True).start()


def _format_recorded_at(recorded_at: str) -> str:
    try:
        dt = datetime.fromisoformat(recorded_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - dt
        minutes = int(diff.total_seconds() // 60)

        if minutes < 1:
            age = "just now"
        elif minutes < 60:
            age = f"{minutes}m ago"
        elif minutes < 1440:
            hours = minutes // 60
            age = f"{hours}h ago"
        else:
            days = minutes // 1440
            age = f"{days}d ago"

        return f"Updated {dt.strftime('%H:%M')}  ·  {age}"
    except Exception:
        return ""


def _safe_update(label: tk.Label, text: str, color: str) -> None:
    try:
        label.config(text=text, fg=color)
    except tk.TclError:
        pass  # widget was destroyed before the thread finished
