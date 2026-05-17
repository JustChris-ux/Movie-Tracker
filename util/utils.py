import requests
import threading
import json
import os
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw

from api.tmdb import WATCHED_FILE
from style import CARD_BG2, TEXT_MUTED
from util.image_loader import image_loader


def star_str(vote):
    try:
        v = float(vote)
        filled = int(v / 2)
        return "★" * filled + "☆" * (5 - filled) + f"  {v:.1f}"
    except Exception:
        return "—"


def fetch_image(url, size=(185, 278)):
    """Blocking download → PIL Image (used by detail backdrop/poster in thread)."""
    try:
        r = requests.get(url, timeout=8)
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        return img
    except Exception:
        return None


def get_image_async(url, size, callback):
    """
    Non-blocking image load.  Delegates to the singleton ImageLoader which
    already holds a reference to the Tk root, so callers do NOT pass root.

    Usage:
        get_image_async(url, (w, h), lambda photo: label.configure(image=photo))
    """
    image_loader.load(url, size, callback)


def load_watched():
    if os.path.exists(WATCHED_FILE):
        with open(WATCHED_FILE, "r") as f:
            return json.load(f)
    save_watched({})
    return {}


def save_watched(data):
    with open(WATCHED_FILE, "w") as f:
        json.dump(data, f, indent=2)


def make_placeholder(size=(185, 278), text="No Image"):
    img = Image.new("RGBA", size, CARD_BG2)
    draw = ImageDraw.Draw(img)
    draw.text((size[0] // 2 - 20, size[1] // 2 - 8), text, fill=TEXT_MUTED)
    return ImageTk.PhotoImage(img)
