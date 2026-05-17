import customtkinter as ctk
import json
import os
from PIL import Image, ImageTk, ImageDraw
from style import *
from views.home import HomePage
from views.details import DetailPage
from views.watched import WatchedPage
from ui.components import *
from api.tmdb import *
from util.utils import *
from util.image_loader import image_loader
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        image_loader.set_root(self)
        self.title("CineTrack")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        self.configure(fg_color=APP_BG)
        self.watched = load_watched()
        self._current = None
        self.show_home()

    def _clear(self):
        if self._current:
            self._current.destroy()
            self._current = None

    def show_home(self):
        self._clear()
        p = HomePage(self, self)
        p.pack(fill="both", expand=True)
        self._current = p

    def show_detail(self, item, media_type):
        self._clear()
        p = DetailPage(self, self, item, media_type)
        p.pack(fill="both", expand=True)
        self._current = p

    def show_watched(self):
        self._clear()
        p = WatchedPage(self, self)
        p.pack(fill="both", expand=True)
        self._current = p
