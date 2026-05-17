import customtkinter as ctk
from style import APP_BG, BORDER, PRIMARY


class ScrollFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kw):
        super().__init__(
            master,
            fg_color=APP_BG,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=PRIMARY,
            **kw,
        )
