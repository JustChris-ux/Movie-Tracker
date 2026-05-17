import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

from style import CARD_BG, CARD_BG2, PRIMARY, BORDER, TEXT_PRIMARY, TEXT_MUTED
from api.tmdb import IMG_BASE_W
from util.utils import get_image_async, make_placeholder, star_str

# Poster is 2:3 ratio
POSTER_RATIO = 278 / 185


class MovieCard(ctk.CTkFrame):
    def __init__(self, master, item, media_type, on_click, watched_ids, **kw):
        self._card_w = kw.pop("width", 185)
        self._card_h = int(self._card_w * POSTER_RATIO)

        super().__init__(
            master,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            width=self._card_w,
            **kw,
        )

        self.item        = item
        self.media_type  = media_type
        self.on_click    = on_click
        self.watched_ids = watched_ids

        # animation state
        self._hover      = False
        self._anim_alpha = 0        # current overlay alpha 0–80
        self._anim_id    = None

        self._build()

    # ── build ──────────────────────────────────────────────────────────────────
    def _build(self):
        item  = self.item
        title = item.get("title") or item.get("name") or "Unknown"
        year  = (item.get("release_date") or item.get("first_air_date") or "")[:4]
        vote  = item.get("vote_average", 0)
        pp    = item.get("poster_path")
        w, h  = self._card_w, self._card_h

        # ── tk.Canvas for the poster ──────────────────────────────────────────
        # fill="x" + padx=0 → canvas spans the card edge-to-edge with zero gaps.
        # CTkLabel adds internal ipadx/ipady; tk.Canvas does not.
        self._canvas = tk.Canvas(
            self,
            width=w, height=h,
            bg=CARD_BG2,
            highlightthickness=0,
            cursor="hand2",
        )
        self._canvas.pack(fill="x", padx=0, pady=0)

        if pp:
            get_image_async(
                f"{IMG_BASE_W}{pp}", (w, h),
                self._on_poster_loaded,
            )
        else:
            ph = make_placeholder((w, h))
            self._canvas.create_image(0, 0, anchor="nw", image=ph)
            self._canvas._ph = ph

        # ── watched badge drawn on canvas ─────────────────────────────────────
        wid = f"{self.media_type}_{item['id']}"
        if wid in self.watched_ids:
            self._canvas.create_rectangle(
                6, 6, 88, 21,
                fill=PRIMARY, outline="", tags="badge")
            self._canvas.create_text(
                47, 14, text="✓  Watched",
                font=("Courier", 9, "bold"), fill="#000", tags="badge")

        # ── text info ─────────────────────────────────────────────────────────
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(fill="x", padx=8, pady=(7, 9))

        lbl_title = ctk.CTkLabel(
            info, text=title,
            font=ctk.CTkFont("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY,
            wraplength=w - 18, justify="left", anchor="w",
        )
        lbl_title.pack(fill="x")

        lbl_year = ctk.CTkLabel(
            info, text=year,
            font=ctk.CTkFont("Helvetica", 10),
            text_color=TEXT_MUTED, anchor="w",
        )
        lbl_year.pack(fill="x")

        lbl_stars = ctk.CTkLabel(
            info, text=star_str(vote),
            font=ctk.CTkFont("Helvetica", 10),
            text_color=PRIMARY, anchor="w",
        )
        lbl_stars.pack(fill="x")

        # ── bindings ──────────────────────────────────────────────────────────
        for widget in [self, self._canvas, info, lbl_title, lbl_year, lbl_stars]:
            widget.bind("<Enter>",    self._on_enter, add="+")
            widget.bind("<Leave>",    self._on_leave, add="+")
            widget.bind("<Button-1>", self._on_click, add="+")

    # ── callbacks ─────────────────────────────────────────────────────────────
    def _on_poster_loaded(self, photo):
        if not photo:
            return
        self._canvas._poster = photo            # keep ref
        self._canvas.create_image(0, 0, anchor="nw", image=photo, tags="poster")
        self._canvas.tag_raise("badge")

    def _on_click(self, _=None):
        self.on_click(self.item, self.media_type)

    # ── hover ─────────────────────────────────────────────────────────────────
    def _on_enter(self, _=None):
        self._hover = True
        self.configure(border_color=PRIMARY)
        self._animate()

    def _on_leave(self, _=None):
        self._hover = False
        self.configure(border_color=BORDER)
        self._animate()

    # ── animation (~60 fps) ───────────────────────────────────────────────────
    def _animate(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None

        TARGET = 75 if self._hover else 0
        STEP   = 9                              # alpha units per frame

        diff = TARGET - self._anim_alpha
        if abs(diff) <= STEP:
            self._anim_alpha = TARGET
        else:
            self._anim_alpha += STEP if diff > 0 else -STEP

        self._draw_overlay()

        if self._anim_alpha != TARGET:
            self._anim_id = self.after(16, self._animate)

    # ── overlay ───────────────────────────────────────────────────────────────
    def _draw_overlay(self):
        self._canvas.delete("overlay")

        a = self._anim_alpha
        if a <= 0:
            return

        w, h = self._card_w, self._card_h

        # lime tint
        tint      = Image.new("RGBA", (w, h), (28, 31, 35, a+70))
        tk_tint   = ImageTk.PhotoImage(tint)
        self._canvas._tint = tk_tint            # must hold ref
        self._canvas.create_image(0, 0, anchor="nw", image=tk_tint, tags="overlay")

        # "View Details" pill — fades in after tint is ~1/3 visible
        if a > 24:
            pill_w, pill_h = 122, 32
            px = w // 2 - pill_w // 2
            py = h // 2 - pill_h // 2

            
            

        # badge always on top
        self._canvas.tag_raise("badge")