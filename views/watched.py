import customtkinter as ctk
import tkinter as tk
import threading
import datetime
from style import *
from ui.components.card import MovieCard
from ui.components.banner import BannerSlider
from ui.components.scroll import ScrollFrame
from api.tmdb import *
from PIL import Image, ImageDraw
from util.utils import *
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class WatchedPage(ctk.CTkFrame):
    def __init__(self, master, app, **kw):
        super().__init__(master, fg_color=APP_BG, **kw)
        self.app = app
        self._build()

    def _build(self):
        # Top bar
        topbar = ctk.CTkFrame(self, fg_color=CARD_BG, height=60, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkButton(topbar, text="← Back", fg_color="transparent",
                      hover_color=CARD_BG2, text_color=PRIMARY,
                      command=self.app.show_home,
                      font=ctk.CTkFont("Helvetica", 14, "bold")).pack(side="left", padx=16)
        ctk.CTkLabel(topbar, text="🎬  CineTrack", font=ctk.CTkFont("Helvetica", 20, "bold"),
                     text_color=PRIMARY).pack(side="left", padx=8)

        # Count badge
        count = len(self.app.watched)
        ctk.CTkLabel(topbar, text=f"{count} watched",
                     font=ctk.CTkFont("Helvetica", 13),
                     text_color=TEXT_MUTED).pack(side="right", padx=20)

        # Header
        ctk.CTkLabel(self, text="✓  My Watched List",
                     font=ctk.CTkFont("Helvetica", 24, "bold"),
                     text_color=PRIMARY).pack(anchor="w", padx=32, pady=(20, 8))

        if not self.app.watched:
            ctk.CTkLabel(self, text="Nothing watched yet.\nStart exploring movies & series!",
                         font=ctk.CTkFont("Helvetica", 16),
                         text_color=TEXT_MUTED, justify="center").pack(expand=True)
            return

        scroll = ScrollFrame(self, orientation="vertical")
        scroll.pack(fill="both", expand=True)

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x", padx=32, pady=8)

        cols = 6
        for i, (wid, entry) in enumerate(self.app.watched.items()):
            # Build a minimal item dict for the card
            fake = {
                "id": entry["id"],
                "title": entry.get("title"),
                "name": entry.get("title"),
                "poster_path": entry.get("poster_path"),
                "vote_average": entry.get("vote_average", 0),
                "release_date": entry.get("release_date"),
                "first_air_date": entry.get("release_date"),
                "overview": entry.get("overview", ""),
            }
            mt = entry.get("media_type", "movie")
            card = MovieCard(grid, fake, mt, self.app.show_detail,
                             self.app.watched, width=185)
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="n")

            # Added date
            added = entry.get("added", "")[:10]
            if added:
                ctk.CTkLabel(grid, text=f"Added {added}",
                             font=ctk.CTkFont("Helvetica", 9),
                             text_color=TEXT_MUTED).grid(
                    row=(i // cols) * 2 + 1, column=i % cols,
                    padx=8, sticky="n")
