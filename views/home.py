

import customtkinter as ctk
import tkinter as tk
import threading
from style import *
from ui.components.card import MovieCard
from ui.components.banner import BannerSlider
from ui.components.scroll import ScrollFrame
from api.tmdb import *
from PIL import Image, ImageDraw
from util.utils import *
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class HomePage(ctk.CTkFrame):
    def __init__(self, master, app, **kw):
        super().__init__(master, fg_color=APP_BG, **kw)
        self.app = app
        self._build()
        self._load_data()

    def _build(self):
        # Top bar
        topbar = ctk.CTkFrame(self, fg_color=CARD_BG, height=60, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="🎬  CineTrack", font=ctk.CTkFont("Helvetica", 20, "bold"),
                     text_color=PRIMARY).pack(side="left", padx=20)

        # Search
        search_frame = ctk.CTkFrame(topbar, fg_color=CARD_BG2, corner_radius=20, height=36)
        search_frame.pack(side="left", padx=20, pady=12, fill="x", expand=True)
        search_frame.pack_propagate(False)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var,
                                         placeholder_text="Search movies & series…",
                                         fg_color="transparent", border_width=0,
                                         text_color=TEXT_PRIMARY,
                                         font=ctk.CTkFont("Helvetica", 13))
        self.search_entry.pack(fill="both", expand=True, padx=12)

        ctk.CTkButton(topbar, text="✓ Watched", fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
                      text_color="#000", command=lambda: self.app.show_watched(),
                      font=ctk.CTkFont("Helvetica", 13, "bold"),
                      corner_radius=20).pack(side="right", padx=8)

        # Scroll area
        self.scroll = ScrollFrame(self, orientation="vertical")
        self.scroll.pack(fill="both", expand=True)

        # Banner
        self.banner = BannerSlider(self.scroll, on_click=self.app.show_detail)
        self.banner.pack(fill="x", padx=0, pady=(0, 24))

        # Sections
        self._section_trending = self._make_section("🔥 Trending Now")
        self._section_popular_m = self._make_section("🎬 Popular Movies")
        self._section_popular_s = self._make_section("📺 Popular Series")

        # Search results (hidden initially)
        self.search_label = ctk.CTkLabel(self.scroll, text="Search Results",
                                         font=ctk.CTkFont("Helvetica", 18, "bold"),
                                         text_color=PRIMARY, anchor="w")
        self.search_frame_outer = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.search_grid = ctk.CTkFrame(self.search_frame_outer, fg_color="transparent")
        self.search_grid.pack(fill="x", padx=20)

        self._search_after = None

    def _make_section(self, title):
        lbl = ctk.CTkLabel(self.scroll, text=title,
                            font=ctk.CTkFont("Helvetica", 18, "bold"),
                            text_color=PRIMARY, anchor="w")
        lbl.pack(fill="x", padx=20, pady=(4, 8))
        sf = ScrollFrame(self.scroll, orientation="horizontal", height=430)
        sf.pack(fill="x", padx=20, pady=(0, 20))
        inner = ctk.CTkFrame(sf, fg_color="transparent")
        inner.pack(fill="y", expand=True)
        return {"label": lbl, "scroll": sf, "inner": inner}

    def _load_data(self):
        def fetch():
            trending = tmdb_get("/trending/all/week") or {}
            pop_m    = tmdb_get("/movie/popular") or {}
            pop_s    = tmdb_get("/tv/popular") or {}

            tr_items = trending.get("results", [])[:15]
            for it in tr_items:
                it["_media_type"] = it.get("media_type", "movie")
            pm_items = pop_m.get("results", [])[:15]
            ps_items = pop_s.get("results", [])[:15]

            self.after(0, lambda: self._populate(tr_items, pm_items, ps_items))
        threading.Thread(target=fetch, daemon=True).start()

    def _populate(self, trending, pop_m, pop_s):
        self.banner.load(trending)
        watched = self.app.watched
        for it in trending:
            mt = it.get("_media_type", "movie")
            card = MovieCard(self._section_trending["inner"], it, mt,
                             self.app.show_detail, watched, width=185)
            card.pack(side="left", padx=6, pady=4)

        for it in pop_m:
            card = MovieCard(self._section_popular_m["inner"], it, "movie",
                             self.app.show_detail, watched, width=185)
            card.pack(side="left", padx=6, pady=4)

        for it in pop_s:
            card = MovieCard(self._section_popular_s["inner"], it, "tv",
                             self.app.show_detail, watched, width=185)
            card.pack(side="left", padx=6, pady=4)

    # ── Search ────────────────────────────────────────────────────────────────
    def _on_search_change(self, *_):
        if self._search_after:
            self.after_cancel(self._search_after)
        q = self.search_var.get().strip()
        if not q:
            self._hide_search()
            return
        self._search_after = self.after(400, lambda: self._do_search(q))

    def _do_search(self, query):
        def fetch():
            res = tmdb_get("/search/multi", {"query": query, "page": 1}) or {}
            items = [r for r in res.get("results", [])
                     if r.get("media_type") in ("movie", "tv")][:20]
            self.after(0, lambda: self._show_search(items))
        threading.Thread(target=fetch, daemon=True).start()

    def _show_search(self, items):
        # Hide sections
        for sec in [self._section_trending, self._section_popular_m, self._section_popular_s]:
            sec["label"].pack_forget()
            sec["scroll"].pack_forget()
        self.banner.pack_forget()

        self.search_label.pack(fill="x", padx=20, pady=(16, 8))
        self.search_frame_outer.pack(fill="x")

        for w in self.search_grid.winfo_children():
            w.destroy()

        watched = self.app.watched
        cols = 6
        for i, it in enumerate(items):
            mt = it.get("media_type", "movie")
            card = MovieCard(self.search_grid, it, mt, self.app.show_detail, watched, width=185)
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="n")

    def _hide_search(self):
        self.search_label.pack_forget()
        self.search_frame_outer.pack_forget()
        self.banner.pack(fill="x", padx=0, pady=(0, 24))
        for sec in [self._section_trending, self._section_popular_m, self._section_popular_s]:
            sec["label"].pack(fill="x", padx=20, pady=(4, 8))
            sec["scroll"].pack(fill="x", padx=20, pady=(0, 20))
