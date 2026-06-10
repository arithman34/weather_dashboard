from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from frontend.constants import BACKGROUND

if TYPE_CHECKING:
    from frontend.page import Page


class PageStack:
    def __init__(self, root):
        self.root = root
        self._stack: list[Page] = []  # This is a private attribute but Python does not enforce it

    def push(self, page_class, **kwargs):
        if self._stack:
            self._stack[-1].pack_forget()

        page = page_class(self.root, self, **kwargs)  # Create the page instance (we might need arguments later btw)
        page.pack(fill="both", expand=True)  # All new pages fill the entire screen both vertically and horizontally
        self._stack.append(page)  # New page is added to the stack
        page.on_show()

    def pop(self):
        if len(self._stack) <= 1:  # Cannot pop as last page is remaining
            return

        top = self._stack.pop()
        top.destroy()

        self._stack[-1].pack(fill="both", expand=True)
        self._stack[-1].on_show()


class ScrollableFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.

    Link: https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
    """

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = tk.Scrollbar(self, orient="vertical")
        vscrollbar.pack(fill="y", side="right", expand=False)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor="nw")

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind("<Configure>", _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind("<Configure>", _configure_canvas)

        def _on_mousewheel(event):
            if interior.winfo_height() > canvas.winfo_height():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
