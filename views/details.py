import customtkinter as ctk
import tkinter as tk
import threading
import datetime
from PIL import Image, ImageTk, ImageDraw

from style import APP_BG, CARD_BG, CARD_BG2, PRIMARY, PRIMARY_HOVER, TEXT_PRIMARY, TEXT_MUTED
from ui.components.scroll import ScrollFrame
from api.tmdb import tmdb_get, IMG_BASE_W, IMG_BASE_O
from util.utils import fetch_image, get_image_async, save_watched, star_str

# ── Cast card dimensions ───────────────────────────────────────────────────────
CAST_CARD_W = 155
CAST_CARD_H = 270
CAST_IMG_H  = 195   # fills full card width — no side gaps

# ── Backdrop height ────────────────────────────────────────────────────────────
BACKDROP_H  = 500


class DetailPage(ctk.CTkFrame):
    def __init__(self, master, app, item, media_type, **kw):
        super().__init__(master, fg_color=APP_BG, **kw)
        self.app           = app
        self.item          = item
        self.media_type    = media_type
        self._backdrop_pil = None
        self._build()
        self._load_details()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # Top bar
        topbar = ctk.CTkFrame(self, fg_color=CARD_BG, height=60, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkButton(
            topbar, text="CineTrack",
            hover="false",
            fg_color="transparent", text_color=PRIMARY,
            command=self.app.show_home,
            font=ctk.CTkFont("Helvetica", 20, "bold"),
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            topbar, text="✓ Watched",
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#000",
            command=self.app.show_watched,
            font=ctk.CTkFont("Helvetica", 13, "bold"), corner_radius=20,
        ).pack(side="right", padx=16)

        self.scroll = ScrollFrame(self, orientation="vertical")
        self.scroll.pack(fill="both", expand=True)

        # Backdrop canvas — 500 px tall; image is scaled-to-width then top-cropped
        self.backdrop_canvas = tk.Canvas(
            self.scroll, bg=APP_BG, highlightthickness=0, height=BACKDROP_H
        )
        self.backdrop_canvas.pack(fill="x")
        self.backdrop_canvas.bind("<Configure>", lambda _e: self._redraw_backdrop())

        # Two-column content
        self.content = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.content.pack(fill="x", padx=32, pady=16)

        # Left: poster + side button
        self.left_col = ctk.CTkFrame(self.content, fg_color="transparent", width=420, height=630)
        self.left_col.pack(side="left", anchor="n", padx=(0, 40))
        self.left_col.pack_propagate(False)

        self.poster_lbl = ctk.CTkLabel(
            self.left_col, text="",
            fg_color="transparent", corner_radius=12,
            width=420, height=630,
        )
        self.poster_lbl.pack(fill="x")

        self.watch_btn = ctk.CTkButton(
            self.left_col, text="＋  Add to Watched",
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#000",
            font=ctk.CTkFont("Helvetica", 13, "bold"),
            corner_radius=20, height=40,
            command=self._toggle_watched,
        )
        self.watch_btn.pack(fill="x", pady=(12, 0))

        # Right: info
        self.right_col = ctk.CTkFrame(self.content, fg_color="transparent")
        self.right_col.pack(side="left", fill="both", expand=True, anchor="n")

        self.title_lbl = ctk.CTkLabel(
            self.right_col, text="Loading…",
            font=ctk.CTkFont("Helvetica", 28, "bold"),
            text_color=TEXT_PRIMARY, anchor="w", wraplength=620,
        )
        self.title_lbl.pack(fill="x", pady=(0, 6))

        self.meta_lbl = ctk.CTkLabel(
            self.right_col, text="",
            font=ctk.CTkFont("Helvetica", 13),
            text_color=PRIMARY, anchor="w",
        )
        self.meta_lbl.pack(fill="x", pady=(0, 12))

        # Prominent CTA button
        btn_row = ctk.CTkFrame(self.right_col, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 14))
        self.watch_btn_main = ctk.CTkButton(
            btn_row, text="＋  Add to Watched",
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#000",
            font=ctk.CTkFont("Helvetica", 15, "bold"),
            corner_radius=24, height=48, width=240,
            command=self._toggle_watched,
        )
        self.watch_btn_main.pack(side="left")

        self.overview_lbl = ctk.CTkLabel(
            self.right_col, text="",
            font=ctk.CTkFont("Helvetica", 12),
            text_color=TEXT_MUTED, anchor="w",
            wraplength=640, justify="left",
        )
        self.overview_lbl.pack(fill="x", pady=(0, 16))

        # Info tiles
        self.info_grid = ctk.CTkFrame(self.right_col, fg_color=CARD_BG, corner_radius=10)
        self.info_grid.pack(fill="x", pady=(0, 20))

        # Cast row
        ctk.CTkLabel(
            self.right_col, text="Cast",
            font=ctk.CTkFont("Helvetica", 16, "bold"),
            text_color=PRIMARY, anchor="w",
        ).pack(fill="x", pady=(8, 4))

        cast_sf = ScrollFrame(self.right_col, orientation="horizontal",
                              height=CAST_CARD_H + 20)
        cast_sf.pack(fill="x")
        self.cast_inner = ctk.CTkFrame(cast_sf, fg_color="transparent")
        self.cast_inner.pack(fill="y")

        self._update_watch_button()

    # ── data loading ──────────────────────────────────────────────────────────
    def _load_details(self):
        item_id = self.item["id"]
        mt      = self.media_type

        def fetch():
            details = tmdb_get(f"/{mt}/{item_id}") or {}
            credits = tmdb_get(f"/{mt}/{item_id}/credits") or {}
            bp      = details.get("backdrop_path") or self.item.get("backdrop_path")
            pp      = details.get("poster_path")   or self.item.get("poster_path")

            # High-res backdrop — cropped to BACKDROP_H in _redraw_backdrop
            backdrop_img = fetch_image(f"{IMG_BASE_O}{bp}", (1920, 1080)) if bp else None
            # Poster fetched at the exact label dimensions (2:3 ratio, no distortion)
            poster_img   = fetch_image(f"{IMG_BASE_W}{pp}", (420, 630))   if pp else None

            cast = credits.get("cast", [])[:10]
            self.after(0, lambda: self._populate(details, backdrop_img, poster_img, cast))

        threading.Thread(target=fetch, daemon=True).start()

    def _populate(self, details, backdrop_img, poster_img, cast):
        title    = details.get("title") or details.get("name") or "Unknown"
        year     = (details.get("release_date") or details.get("first_air_date") or "")[:4]
        vote     = details.get("vote_average", 0)
        runtime  = details.get("runtime") or (details.get("episode_run_time") or [None])[0]
        genres   = ", ".join(g["name"] for g in details.get("genres", []))
        tagline  = details.get("tagline", "")
        overview = details.get("overview", "")
        status   = details.get("status", "")
        lang     = details.get("original_language", "").upper()

        self.title_lbl.configure(text=title)

        meta = f"Released: {year}           Genres:  {genres}"
        if runtime:
            meta += f"   {runtime} min"
        self.meta_lbl.configure(text=meta)

        self.overview_lbl.configure(
            text=(tagline + "\n\n" if tagline else "") + overview
        )

        # Info tiles
        for w in self.info_grid.winfo_children():
            w.destroy()
        info_items = [("Status", status), ("Language", lang),
                      ("Rating", f"{vote:.1f} / 10")]
        if self.media_type == "tv":
            info_items += [("Seasons",  details.get("number_of_seasons",  "—")),
                           ("Episodes", details.get("number_of_episodes", "—"))]
        for col, (k, v) in enumerate(info_items):
            f = ctk.CTkFrame(self.info_grid, fg_color="transparent")
            f.grid(row=0, column=col, padx=20, pady=12, sticky="w")
            ctk.CTkLabel(f, text=k, font=ctk.CTkFont("Helvetica", 10),
                         text_color=TEXT_MUTED).pack(anchor="w")
            ctk.CTkLabel(f, text=str(v), font=ctk.CTkFont("Helvetica", 13, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")

        # Backdrop
        if backdrop_img:
            self._backdrop_pil = backdrop_img
            self._redraw_backdrop()

        # Poster — CTkImage size matches fetch size and label dimensions exactly
        if poster_img:
            ctk_img = ctk.CTkImage(
                light_image=poster_img, dark_image=poster_img, size=(420, 630   )
            )
            self.poster_lbl.configure(image=ctk_img, text="")
            self.poster_lbl.image = ctk_img   # prevent GC

        # Cast
        for member in cast:
            self._add_cast(member)

    # ── backdrop ──────────────────────────────────────────────────────────────
    def _redraw_backdrop(self):
        if self._backdrop_pil is None:
            return

        w   = self.backdrop_canvas.winfo_width() or 1280
        src = self._backdrop_pil

        # Scale so width fills the canvas, then crop to exactly BACKDROP_H from the top
        scale   = w / src.width
        new_h   = int(src.height * scale)
        resized = src.resize((w, new_h), Image.LANCZOS)
        cropped = resized.crop((0, 0, w, BACKDROP_H))

        # Gradient overlay: gentle fade to APP_BG colour at the bottom
        bg_r, bg_g, bg_b = 25, 25, 25
        overlay = Image.new("RGBA", (w, BACKDROP_H), (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)
        for y in range(BACKDROP_H):
            alpha = int(60 + 195 * (y / BACKDROP_H) ** 1.4)
            draw.line([(0, y), (w, y)], fill=(bg_r, bg_g, bg_b, alpha))

        cropped.paste(overlay, mask=overlay)

        tk_img = ImageTk.PhotoImage(cropped)
        self.backdrop_canvas._ref = tk_img
        self.backdrop_canvas.delete("all")
        self.backdrop_canvas.create_image(0, 0, anchor="nw", image=tk_img)

    # ── cast ──────────────────────────────────────────────────────────────────
    def _add_cast(self, member):
        name = member.get("name", "")
        char = member.get("character", "")
        pic  = member.get("profile_path")

        frame = ctk.CTkFrame(
            self.cast_inner,
            fg_color=CARD_BG, corner_radius=14,
            width=CAST_CARD_W, height=CAST_CARD_H,
        )
        frame.pack(side="left", padx=6, pady=4)
        frame.pack_propagate(False)

        # Image fills the full card width — zero padx/pady removes the grey side gaps
        img_lbl = ctk.CTkLabel(
            frame, text="",
            width=CAST_CARD_W, height=CAST_IMG_H,
            fg_color=CARD_BG2, corner_radius=0,
        )
        img_lbl.pack(padx=0, pady=0)

        if pic:
            get_image_async(
                f"{IMG_BASE_W}{pic}", (CAST_CARD_W, CAST_IMG_H),
                lambda photo, l=img_lbl: self._set_cast_photo(l, photo),
            )

        ctk.CTkLabel(
            frame, text=name,
            font=ctk.CTkFont("Helvetica", 11, "bold"),
            text_color=TEXT_PRIMARY,
            wraplength=CAST_CARD_W - 10, justify="center",
        ).pack(padx=6, pady=(6, 0))

        ctk.CTkLabel(
            frame, text=char,
            font=ctk.CTkFont("Helvetica", 10),
            text_color=TEXT_MUTED,
            wraplength=CAST_CARD_W - 10, justify="center",
        ).pack(padx=6, pady=(2, 8))

    def _set_cast_photo(self, label, photo):
        if photo:
            label.configure(image=photo)
            label._ref = photo

    # ── watched toggle ────────────────────────────────────────────────────────
    def _toggle_watched(self):
        wid = f"{self.media_type}_{self.item['id']}"
        if wid in self.app.watched:
            del self.app.watched[wid]
        else:
            title = self.item.get("title") or self.item.get("name") or "Unknown"
            self.app.watched[wid] = {
                "id":           self.item["id"],
                "media_type":   self.media_type,
                "title":        title,
                "poster_path":  self.item.get("poster_path"),
                "vote_average": self.item.get("vote_average"),
                "release_date": (self.item.get("release_date") or
                                 self.item.get("first_air_date")),
                "overview":     self.item.get("overview"),
                "added":        datetime.datetime.now().isoformat(),
            }
        save_watched(self.app.watched)
        self._update_watch_button()

    def _update_watch_button(self):
        wid = f"{self.media_type}_{self.item['id']}"
        if wid in self.app.watched:
            cfg = dict(text="✓  In Watched List",
                       fg_color=CARD_BG2, hover_color="#3a3a3a",
                       text_color=PRIMARY)
        else:
            cfg = dict(text="＋  Add to Watched",
                       fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
                       text_color="#000")
        self.watch_btn.configure(**cfg)
        if hasattr(self, "watch_btn_main"):
            self.watch_btn_main.configure(**cfg)
