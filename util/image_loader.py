# util/image_loader.py

import requests
import threading
from io import BytesIO
from PIL import Image, ImageTk

class ImageLoader:
    _instance = None

    def __new__(cls, root=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.root = root
            cls._instance.cache = {}
        return cls._instance

    def set_root(self, root):
        self.root = root

    # ---- background download ----
    def _download(self, url, size):
        try:
            r = requests.get(url, timeout=8)
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            return img
        except Exception:
            return None

    # ---- public loader ----
    def load(self, url, size, callback):
        key = (url, size)

        if key in self.cache:
            callback(self.cache[key])
            return

        def worker():
            pil_img = self._download(url, size)

            if pil_img is None:
                return

            # ⚠️ PhotoImage MUST be created on UI thread
            def create_photo():
                photo = ImageTk.PhotoImage(pil_img)
                self.cache[key] = photo
                callback(photo)

            self.root.after(0, create_photo)

        threading.Thread(target=worker, daemon=True).start()


image_loader = ImageLoader()
