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

        # State
        self._current_mode = None      # None | "search" | "browse"
        self._current_page = 1
        self._current_total_pages = 1
        self._search_query = ""
        self._browse_section_id = None

        self._build()
        self._load_data()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # ── Top bar ──────────────────────────────────────────────────────────
        topbar = ctk.CTkFrame(self, fg_color=CARD_BG, height=60, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkButton(
            topbar, text="CineTrack",
            font=ctk.CTkFont("Helvetica", 20, "bold"),
            text_color=PRIMARY,
            height=36,
            fg_color="transparent",      
            hover=False,
            command=self._hide_results
        ).pack(side="left", padx=20)

        # Search entry
        search_frame = ctk.CTkFrame(topbar, fg_color=CARD_BG2, corner_radius=20, height=36)
        search_frame.pack(side="left", padx=(20, 6), pady=12, fill="x", expand=True)
        search_frame.pack_propagate(False)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search movies & series…",
            fg_color="transparent",
            border_width=0,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont("Helvetica", 13),
        )
        self.search_entry.pack(fill="both", expand=True, padx=12)
        # Trigger on Enter key as well
        self.search_entry.bind("<Return>", lambda _e: self._trigger_search())

        # Search button (manual trigger – no auto-search on typing)
        ctk.CTkButton(
            topbar,
            text="🔍",
            fg_color=CARD_BG2,
            hover_color="#3A3A3A",
            text_color=PRIMARY,
            font=ctk.CTkFont("Helvetica", 20, "bold"),
            corner_radius=20,
            height=35,
            width=15,
            border_width=2,
            border_color=PRIMARY_HOVER,
            command=self._trigger_search,
        ).pack(side="left", pady=(8,8))

        ctk.CTkButton(
            topbar,
            text="✓ Watched",
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color="#000",
            command=lambda: self.app.show_watched(),
            font=ctk.CTkFont("Helvetica", 13, "bold"),
            height=34,
            corner_radius=20,
        ).pack(side="right", padx=12)

        # ── Scrollable body ───────────────────────────────────────────────────
        self.scroll = ScrollFrame(self, orientation="vertical")
        self.scroll.pack(fill="both", expand=True)

        # Banner (home only)
        self.banner = BannerSlider(self.scroll, on_click=self.app.show_detail)
        self.banner.pack(fill="x", padx=0, pady=(0, 24))

        # Home sections
        self._section_trending  = self._make_section("🔥 Trending Now",    "trending")
        self._section_popular_m = self._make_section("🎬 Popular Movies",  "popular_movie")
        self._section_popular_s = self._make_section("📺 Popular Series",  "popular_tv")

        # Results area (search + browse-all share this)
        self._build_results_area()

    def _make_section(self, title, section_id):
        """Create a labelled horizontal scroll section with a Browse All button."""
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(4, 4))

        lbl = ctk.CTkLabel(
            header, text=title,
            font=ctk.CTkFont("Helvetica", 18, "bold"),
            text_color=PRIMARY,
            anchor="w",
        )
        lbl.pack(side="left")

        browse_btn = ctk.CTkButton(
            header,
            text="Browse All  →",
            fg_color="transparent",
            hover_color="#a5d045",
            text_color="#fff",
            font=ctk.CTkFont("Helvetica", 16, "bold"),
            corner_radius=20,
            
            height=40,
            border_width=1,
            border_color="#a8c55c",
            command=lambda sid=section_id: self._browse_all(sid),
        )
        browse_btn.pack(side="right", padx=10)

        sf = ScrollFrame(self.scroll, orientation="horizontal", height=430)
        sf.pack(fill="x", padx=20, pady=(4, 20))

        inner = ctk.CTkFrame(sf, fg_color="transparent")
        inner.pack(fill="y", expand=True)

        return {"header": header, "scroll": sf, "inner": inner}

    def _build_results_area(self):
        """
        Shared header + grid used by both search results and browse-all.
        Kept pack_forget-ed until needed.
        """
        # ── Results header ────────────────────────────────────────────────────
        self.results_header = ctk.CTkFrame(self.scroll, fg_color="transparent")

        # Back / title row
        title_row = ctk.CTkFrame(self.results_header, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 4))

        title_row.grid_columnconfigure(0, weight=1)
        title_row.grid_columnconfigure(1, weight=1)
        title_row.grid_columnconfigure(2, weight=1)

        


        self.results_title_lbl = ctk.CTkLabel(
            title_row,
            text="",
            font=ctk.CTkFont("Helvetica", 22, "bold"),
            text_color=PRIMARY,
            anchor="center",
            justify="center",
        )
        self.results_title_lbl.grid(row=0, column=1)
        self.results_title_lbl.grid_columnconfigure(0, weight=1)

       
        self.results_outer = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.results_grid  = ctk.CTkFrame(self.results_outer, fg_color="transparent")
        self.results_grid.pack(fill="both", expand=True, padx=(50,50))

        self.page_row = ctk.CTkFrame(
            self.results_header,
            fg_color="transparent"
        )
        self.page_row.pack(fill="x", pady=(4, 0), padx=(10,0))

        # Center layout
        for i in range(3):
            self.page_row.grid_columnconfigure(i, weight=1)

        self.prev_btn = ctk.CTkButton(
            self.page_row,
            text="← Prev",
            fg_color=CARD_BG2,
            hover_color="#3a3a3a",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont("Helvetica", 16),
            corner_radius=20,
            width=95,
            command=self._prev_page,
        )
        self.prev_btn.grid(row=0, column=1, padx=40, sticky="w")

        self.page_lbl = ctk.CTkLabel(
            self.page_row,
            text="Page 1 / 1",
            font=ctk.CTkFont("Helvetica", 16),
            text_color=TEXT_MUTED,
            width=100,
        )
        self.page_lbl.grid(row=0, column=1, padx=40)

        self.next_btn = ctk.CTkButton(
            self.page_row,
            text="Next →",
            fg_color=CARD_BG2,
            hover_color="#3a3a3a",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont("Helvetica", 16),
            corner_radius=20,
            width=95,
            command=self._next_page,
        )
        self.next_btn.grid(row=0, column=1, padx=40, sticky="e")
    # ── Data loading ──────────────────────────────────────────────────────────

    def _load_data(self):
        def fetch():
            trending = tmdb_get("/trending/all/week") or {}
            pop_m    = tmdb_get("/movie/popular")     or {}
            pop_s    = tmdb_get("/tv/popular")        or {}

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

    # ── Browse All ────────────────────────────────────────────────────────────

    _BROWSE_CONFIG = {
        "trending": {
            "endpoint":   "/trending/all/week",
            "title":      "🔥 Trending Now",
            "media_type": None,           # uses item-level media_type
        },
        "popular_movie": {
            "endpoint":   "/movie/popular",
            "title":      "🎬 Popular Movies",
            "media_type": "movie",
        },
        "popular_tv": {
            "endpoint":   "/tv/popular",
            "title":      "📺 Popular Series",
            "media_type": "tv",
        },
    }

    def _browse_all(self, section_id):
        self._browse_section_id = section_id
        self._current_mode = "browse"
        self._current_page = 1
        self._fetch_browse_page()

    def _fetch_browse_page(self):
        cfg      = self._BROWSE_CONFIG[self._browse_section_id]
        endpoint = cfg["endpoint"]
        page     = self._current_page
        mt_fixed = cfg["media_type"]

        def fetch():
            data        = tmdb_get(endpoint, {"page": page}) or {}
            items       = data.get("results", [])
            total_pages = min(data.get("total_pages", 1), 500)  # TMDB hard-caps at 500

            for it in items:
                it["_media_type"] = mt_fixed if mt_fixed else it.get("media_type", "movie")

            # Sort: higher vote_average first (most relevant / rated)
            items.sort(key=lambda x: x.get("vote_average", 0), reverse=True)

            self.after(0, lambda: self._render_results(
                items, cfg["title"], page, total_pages))

        threading.Thread(target=fetch, daemon=True).start()

    # ── Search ────────────────────────────────────────────────────────────────

    def _trigger_search(self):
        q = self.search_var.get().strip()
        if not q:
            if self._current_mode is not None:
                self._hide_results()
            return
        self._search_query  = q
        self._current_mode  = "search"
        self._current_page  = 1
        self._fetch_search_page()

    def _fetch_search_page(self):
        query = self._search_query
        page  = self._current_page

        def fetch():
            res   = tmdb_get("/search/multi", {"query": query, "page": page}) or {}
            items = [r for r in res.get("results", [])
                     if r.get("media_type") in ("movie", "tv")]
            total_pages = min(res.get("total_pages", 1), 500)

            # More relevant first: popularity desc (TMDB default), but bump exact title matches
            title_q = query.lower()
            items.sort(
                key=lambda x: (
                    -(1 if title_q in (x.get("title") or x.get("name") or "").lower() else 0),
                    -x.get("popularity", 0),
                ),
            )

            for it in items:
                it["_media_type"] = it.get("media_type", "movie")

            self.after(0, lambda: self._render_results(
                items, f'Search: "{query}"', page, total_pages))

        threading.Thread(target=fetch, daemon=True).start()

    # ── Shared results renderer ───────────────────────────────────────────────

    def _render_results(self, items, title, page, total_pages):
        self._current_page        = page
        self._current_total_pages = total_pages

        # Hide home content
        self._set_sections_visible(False)

        # Update header labels
        self.results_title_lbl.configure(text=title)
        self.page_lbl.configure(text=f"Page {page} / {total_pages}")
        self.prev_btn.configure(state="normal" if page > 1            else "disabled")
        self.next_btn.configure(state="normal" if page < total_pages  else "disabled")

        # Show results area
        self.results_header.pack(fill="x", padx=16, pady=(16, 0))
        self.results_outer.pack(fill="both", expand=True)

        # Clear old cards
        for w in self.results_grid.winfo_children():
            w.destroy()

        # Dynamic column count based on window width
        self.update_idletasks()
        win_w = self.winfo_width() or 1280
        card_w = 185 + 16          # card width + 2×padx
        cols   = max(2, win_w // card_w)

        watched = self.app.watched
        for i, it in enumerate(items):
            mt   = it.get("_media_type", "movie")
            card = MovieCard(self.results_grid, it, mt,
                             self.app.show_detail, watched, width=185)
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="n")

    # ── Pagination ────────────────────────────────────────────────────────────

    def _prev_page(self):
        if self._current_page <= 1:
            return
        self._current_page -= 1
        self._go_to_current_page()

    def _next_page(self):
        if self._current_page >= self._current_total_pages:
            return
        self._current_page += 1
        self._go_to_current_page()

    def _go_to_current_page(self):
        # Scroll back to top of results
        if hasattr(self.scroll, "_canvas"):
            self.scroll._canvas.yview_moveto(0)

        if self._current_mode == "search":
            self._fetch_search_page()
        elif self._current_mode == "browse":
            self._fetch_browse_page()

    # ── Show / hide helpers ───────────────────────────────────────────────────

    def _set_sections_visible(self, visible):
        if visible:
            self.banner.pack(fill="x", padx=0, pady=(0, 24))
            for sec in [self._section_trending,
                        self._section_popular_m,
                        self._section_popular_s]:
                sec["header"].pack(fill="x", padx=20, pady=(4, 4))
                sec["scroll"].pack(fill="x", padx=20, pady=(4, 20))
        else:
            self.banner.pack_forget()
            for sec in [self._section_trending,
                        self._section_popular_m,
                        self._section_popular_s]:
                sec["header"].pack_forget()
                sec["scroll"].pack_forget()

    def _hide_results(self):
        self.results_header.pack_forget()
        self.results_outer.pack_forget()
        self._current_mode = None
        self._set_sections_visible(True)
