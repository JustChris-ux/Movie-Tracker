import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw

from style import APP_BG, CARD_BG, PRIMARY, BORDER, TEXT_PRIMARY, TEXT_MUTED
from api.tmdb import IMG_BASE_O
from util.utils import get_image_async, star_str

BANNER_RATIO = 16 / 9


class BannerSlider(ctk.CTkFrame):
    """Full-width cinematic banner with prev/next arrows drawn on the canvas."""

    def __init__(self, master, on_click, **kw):
        super().__init__(master, fg_color="transparent", **kw)        
        self.on_click  = on_click
        self.items     = []
        self.idx       = 0
        self._imgs     = {}
        self._after_id = None
        self._prev_hover = False
        self._next_hover = False
        self._build()

    # ── build ─────────────────────────────────────────────────────────────────
    def _build(self):
        self.canvas = tk.Canvas(self, bg=APP_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", self._on_leave)
        self.canvas.bind("<Button-1>", self._on_click)
    def _on_resize(self, event):
        w = event.width
        h = int(w / BANNER_RATIO)

        self.configure(height=h)
        self.canvas.configure(height=h)

        self._draw_banner()
    # ── data ──────────────────────────────────────────────────────────────────
    def load(self, items):
        self.items = items
        self.idx   = 0
        for it in items[:8]:
            bp = it.get("backdrop_path")
            if bp:
                # 3-arg — root handled inside get_image_async via image_loader
                w = self.winfo_width() or 1280
                h = int(w / BANNER_RATIO)

                get_image_async(
                    f"{IMG_BASE_O}{bp}",
                    (w, h),
                    lambda img, i=it: self._store_img(i, img),
                )
        self._draw_banner()
        self._schedule()

    def _store_img(self, item, img):
        self._imgs[item["id"]] = img
        if self.items and item["id"] == self.items[self.idx]["id"]:
            self._draw_banner()

    # ── draw ──────────────────────────────────────────────────────────────────
    def _draw_banner(self):
        self.canvas.delete("all")
        if not self.items:
            return

        item = self.items[self.idx]
        w    = self.canvas.winfo_width() or 900
        h = self.canvas.winfo_height()

        # backdrop
        img = self._imgs.get(item["id"])
        if img:
            pil = ImageTk.getimage(img).resize((w, h), Image.LANCZOS)
            ov  = Image.new("RGBA", (w, h))
            dr  = ImageDraw.Draw(ov)
            for y in range(h):
                frac  = y / h
                alpha = int(max(0, (frac - 0.30) / 0.70) * 215)
                dr.line([(0, y), (w, y)], fill=(25, 25, 25, alpha))
            pil.paste(ov, mask=ov)
            tk_img = ImageTk.PhotoImage(pil)
            self.canvas._banner_ref = tk_img
            self.canvas.create_image(0, 0, anchor="nw", image=tk_img)
        else:
            self.canvas.create_rectangle(0, 0, w, h, fill=CARD_BG, outline="")

        # text overlay
        title    = item.get("title") or item.get("name") or ""
        overview = (item.get("overview") or "")[:200]
        if len(item.get("overview", "")) > 200:
            overview += "…"
        vote  = item.get("vote_average", 0)
        year  = (item.get("release_date") or item.get("first_air_date") or "")[:4]
        mt    = item.get("_media_type", "movie")
        badge = "🎬 MOVIE" if mt == "movie" else "📺 SERIES"

        # original h - 218 becomes h - 288 | original h - 198 becomes h - 268
        self.canvas.create_rectangle(40, h - 288, 130, h - 268, fill=PRIMARY, outline="")

# original h - 208 becomes h - 278
        self.canvas.create_text(85, h - 278, text=badge, anchor="center",
                        font=("Helvetica", 9, "bold"), fill="#000")
        self.canvas.create_text(40, h - 188, text=title, anchor="sw",
                                font=("Helvetica", 34, "bold"), fill=TEXT_PRIMARY, width=w - 80)
        self.canvas.create_text(40, h - 154, text=f"{year}   {star_str(vote)}", anchor="sw",
                                font=("Helvetica", 14), fill=PRIMARY)
        self.canvas.create_text(40, h - 64, text=overview, anchor="sw",
                                font=("Helvetica", 12), fill=TEXT_MUTED, width=w - 100)

        # dots
        total = min(len(self.items), 8)
        dot_x = w // 2 - (total * 16) // 2
        for i in range(total):
            color = PRIMARY if i == self.idx else BORDER
            r     = 5 if i == self.idx else 4
            cx    = dot_x + i * 16 + 5
            self.canvas.create_oval(cx - r, h - 14 - r, cx + r, h - 14 + r,
                                    fill=color, outline="")

        # arrow circles (drawn on canvas — no square CTkButton background)
        self._draw_banner_arrows(w, h)

    def _draw_banner_arrows(self, w, h):
        cy  = h // 2
        r   = 22
        pad = 28

        for side in ("prev", "next"):
            cx        = pad if side == "prev" else w - pad
            hovered   = self._prev_hover if side == "prev" else self._next_hover
            glyph     = "‹" if side == "prev" else "›"
            fill      = PRIMARY if hovered else "#000000"
            txt_color = "#000" if hovered else TEXT_PRIMARY
            tag       = f"{side}_btn"

            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=fill, outline=PRIMARY, width=1.5, tags=tag)
            self.canvas.create_text(cx, cy, text=glyph,
                                    font=("Helvetica", 22, "bold"),
                                    fill=txt_color, tags=tag)

        self._arrow_prev_cx = pad
        self._arrow_next_cx = w - pad
        self._arrow_cy      = cy
        self._arrow_r       = r

    # ── hit testing ───────────────────────────────────────────────────────────
    def _hit(self, x, y, cx):
        try:
            return (x - cx) ** 2 + (y - self._arrow_cy) ** 2 <= self._arrow_r ** 2
        except AttributeError:
            return False

    def _on_motion(self, event):
        prev = self._hit(event.x, event.y, self._arrow_prev_cx) if hasattr(self, "_arrow_prev_cx") else False
        nxt  = self._hit(event.x, event.y, self._arrow_next_cx) if hasattr(self, "_arrow_next_cx") else False
        if prev != self._prev_hover or nxt != self._next_hover:
            self._prev_hover = prev
            self._next_hover = nxt
            self._draw_banner()

    def _on_leave(self, event):
        if self._prev_hover or self._next_hover:
            self._prev_hover = False
            self._next_hover = False
            self._draw_banner()

    def _on_click(self, event):
        if hasattr(self, "_arrow_prev_cx") and self._hit(event.x, event.y, self._arrow_prev_cx):
            self._prev()
        elif hasattr(self, "_arrow_next_cx") and self._hit(event.x, event.y, self._arrow_next_cx):
            self._next()
        elif self.items:
            item = self.items[self.idx]
            self.on_click(item, item.get("_media_type", "movie"))

    # ── navigation ────────────────────────────────────────────────────────────
    def _prev(self):
        self._cancel()
        self.idx = (self.idx - 1) % min(len(self.items), 8)
        self._draw_banner()
        self._schedule()

    def _next(self):
        self._cancel()
        self.idx = (self.idx + 1) % min(len(self.items), 8)
        self._draw_banner()
        self._schedule()

    def _schedule(self):
        self._after_id = self.after(5000, self._auto)

    def _cancel(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _auto(self):
        self.idx = (self.idx + 1) % min(len(self.items), 8)
        self._draw_banner()
        self._schedule()
