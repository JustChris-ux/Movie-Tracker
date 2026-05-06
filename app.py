import json
from customtkinter import *
from tkinter import filedialog, Canvas
import os
import shutil
from datetime import datetime
from PIL import Image, ImageDraw

set_appearance_mode("dark")

class MovieApp(CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.geometry("1250x750")
        self.title("My Movie Collection")
        
        # Paths
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(current_path, "mydata.json")
        self.assets_dir = os.path.join(current_path, "assets")
        self.images_dir = os.path.join(self.assets_dir, "posters")
        self.icons_dir = os.path.join(self.assets_dir, "icons")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.icons_dir, exist_ok=True)

        # Image state for current movie
        self.selected_image_path = None
        self.edit_movie_index = None

        self.load_data()
        
        # App color base
        self.configure(fg_color="#191919")
        self.std_btn_height = 34
        self.std_btn_font = ("Arial", 12, "bold")
        self.startup_splash = None
        self.startup_loading_label = None
        self.startup_loading_job = None
        self.startup_logo_image = None
        self._ctk_image_cache = {}
        self._movies_page_last_signature = None
        self._movies_page_last_width = 0
        self._details_resize_job = None
        self._details_last_render_key = None
        self._home_cards_resize_job = None
        self._home_cards_settle_job = None
        self._home_cards_last_width = 0
        self._home_cards_last_render_key = None
        self.home_icon_image = self._create_icon_from_png(
            os.path.join(self.icons_dir, "home.png"),
            size=16
        )
        self.search_icon_image = self._create_icon_from_png(
            os.path.join(self.icons_dir, "search.png"),
            size=16
        )
        self.menu_icon_image = self._create_icon_from_png(
            os.path.join(self.icons_dir, "menu.png"),
            size=16
        )
        self.world_top5_paths = [
            os.path.join(self.assets_dir, "top5", "shawshank.jpg"),
            os.path.join(self.assets_dir, "top5", "godfather.jpg"),
            os.path.join(self.assets_dir, "top5", "schindler.jpg"),
            os.path.join(self.assets_dir, "top5", "fightclub.jpg"),
            os.path.join(self.assets_dir, "top5", "forrestgump.jpg"),
        ]

        # Create main container
        self.main_container = CTkFrame(self, fg_color="#1f1f1f", corner_radius=16)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_view = CTkTabview(self.main_container, width=850, height=500, fg_color=("black", "#252525"), segmented_button_fg_color="#8b0000", segmented_button_selected_color="#a52a2a")
        self.tab_view.pack(pady=0, padx=(0,0), fill="both", expand=True)
        self.tab_view.add("Add Movie")
        self.tab_view.add("Movie List")
        self.tab_view.add("Movies Page")
        self.tab_view.add("Movie Details")
        
        # Setup each tab
        self.setup_add_movie_tab()
        self.setup_movie_list_tab()
        self.setup_movies_page_tab()
        self.setup_movie_details_tab()
        # Hide default tab buttons: screenshots use only side navigation.
        self.tab_view._segmented_button.grid_remove()
        self.tab_view.set("Movie List")
        self._show_startup_splash()
        self.after(1200, self._hide_startup_splash)
    
    def load_data(self):
        """Load movie data from JSON file"""
        self.data = {"movies": [], "journal_note": ""}
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.data = json.load(file)
        if not isinstance(self.data, dict):
            self.data = {"movies": [], "journal_note": ""}
        self.data.setdefault("movies", [])
        self.data.setdefault("journal_note", "")
    
    def save_data(self):
        """Save movie data to JSON file"""
        with open(self.data_file, "w") as file:
            json.dump(self.data, file, indent=4)

    def _show_startup_splash(self):
        """Show startup splash to hide initial layout/rendering jitter."""
        self.startup_splash = CTkFrame(self, fg_color="#161616", corner_radius=0)
        self.startup_splash.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.startup_splash.lift()

        center = CTkFrame(self.startup_splash, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = os.path.join(self.assets_dir, "app-logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path).convert("RGBA")
                logo_img.thumbnail((250, 250), Image.Resampling.LANCZOS)
                logo_size = logo_img.size
                self.startup_logo_image = CTkImage(light_image=logo_img, dark_image=logo_img, size=logo_size)
                CTkLabel(center, text="", image=self.startup_logo_image).pack(pady=(0, 14))
            except Exception:
                CTkLabel(center, text="Movie Tracker", font=("Arial", 28, "bold"), text_color="#d4ff60").pack(pady=(0, 14))
        else:
            CTkLabel(center, text="Movie Tracker", font=("Arial", 28, "bold"), text_color="#d4ff60").pack(pady=(0, 14))

        self.startup_loading_label = CTkLabel(
            center,
            text="Loading",
            font=("Arial", 18, "bold"),
            text_color="#e7e7e7"
        )
        self.startup_loading_label.pack()
        self._animate_startup_loading(0)

    def _animate_startup_loading(self, step):
        if not self.startup_loading_label:
            return
        dots = "." * ((step % 3) + 1)
        self.startup_loading_label.configure(text=f"Loading{dots}")
        self.startup_loading_job = self.after(320, lambda: self._animate_startup_loading(step + 1))

    def _hide_startup_splash(self):
        if self.startup_loading_job:
            self.after_cancel(self.startup_loading_job)
            self.startup_loading_job = None
        if self.startup_splash:
            self.startup_splash.destroy()
            self.startup_splash = None
        self.startup_loading_label = None

    def _build_sidebar(self, parent, active_key):
        """Create fixed, centered sidebar with consistent icons."""
        left_menu = CTkFrame(parent, width=72, fg_color="#2c2c2c", corner_radius=12)
        left_menu.pack(side="left", fill="y", padx=(0, 16))
        left_menu.pack_propagate(False)

        buttons_holder = CTkFrame(left_menu, fg_color="transparent")
        buttons_holder.place(relx=0.5, rely=0.5, anchor="center")

        nav_items = [
            ("home", "⌂", lambda: self.tab_view.set("Movie List")),
            ("add", "+", lambda: self.tab_view.set("Add Movie")),
            ("menu", "☰", lambda: self.tab_view.set("Movies Page")),
        ]

        for key, icon, action in nav_items:
            is_active = key == active_key
            btn_text = ""
            btn_image = None
            if key == "home":
                btn_image = self.home_icon_image
            elif key == "menu":
                btn_image = self.menu_icon_image
            else:
                btn_text = icon
            CTkButton(
                buttons_holder,
                text=btn_text,
                image=btn_image,
                width=36,
                height=36,
                corner_radius=8,
                fg_color="#b8e84b" if is_active else "#f0f0f0",
                text_color="black",
                hover_color="#c8f15f" if is_active else "#ffffff",
                font=("Arial", 16, "bold"),
                command=action
            ).pack(pady=9)

        return left_menu
    
    def setup_add_movie_tab(self):
        """Setup the Add Movie tab in the provided 1:1 style."""
        tab = self.tab_view.tab("Add Movie")
        tab.configure(fg_color="#1f1f1f")

        page = CTkFrame(tab, fg_color="#1f1f1f")
        page.pack(fill="both", expand=True, padx=14, pady=14)

        self._build_sidebar(page, "add")

        content = CTkFrame(page, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)

        header = CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(4, 14))
        CTkLabel(header, text="Add new movie", font=("Arial", 22, "bold")).pack(anchor="n")
        CTkLabel(header, text="Track your personal movie collection", font=("Arial", 13), text_color="#b8b8b8").pack(anchor="n", pady=(2, 0))

        body = CTkFrame(content, fg_color="transparent")
        body.pack(fill="both", expand=True)

        left_card = CTkFrame(body, fg_color="#2b2b2b", corner_radius=12)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 14))
        self.add_left_card = left_card
        self.add_left_card.bind("<Configure>", self._on_add_left_card_configure)

        right_card = CTkFrame(body, fg_color="#2b2b2b", corner_radius=12, width=430)
        right_card.pack(side="left", fill="y")
        right_card.pack_propagate(False)

        CTkLabel(left_card, text="About movie", font=("Arial", 22, "bold"), anchor="w").pack(fill="x", padx=24, pady=(18, 12))

        upload_box = CTkFrame(left_card, fg_color="#545454", corner_radius=10)
        upload_box.pack(fill="x", padx=24, pady=(0, 14))
        self.upload_box = upload_box

        self.upload_canvas = Canvas(
            upload_box,
            height=126,
            bg="#545454",
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )
        self.upload_canvas.pack(fill="x", padx=6, pady=6)
        self.upload_border_base_color = "#b8e84b"
        self.upload_border_hover_color = "#d7ff6a"
        self.upload_border_color = self.upload_border_base_color
        self.upload_bg_base_color = "#545454"
        self.upload_bg_hover_color = "#626262"
        self.upload_bg_color = self.upload_bg_base_color
        self.upload_hover_job = None
        self.upload_canvas.bind("<Button-1>", lambda _e: self.choose_image())
        self.upload_canvas.bind("<Configure>", self._draw_upload_placeholder)
        self.upload_canvas.bind("<Enter>", lambda _e: self._animate_upload_hover(self.upload_border_hover_color, self.upload_bg_hover_color))
        self.upload_canvas.bind("<Leave>", lambda _e: self._animate_upload_hover(self.upload_border_base_color, self.upload_bg_base_color))

        self.image_label = CTkLabel(left_card, text="No image selected", font=("Arial", 12), text_color="#b8b8b8", anchor="w")
        self.image_label.pack(fill="x", padx=24, pady=(0, 8))

        CTkLabel(left_card, text="Movie title", anchor="w").pack(fill="x", padx=24, pady=(2, 4))
        self.name_entry = CTkEntry(left_card, height=40, placeholder_text="Enter title...", fg_color="#5a5a5a", border_width=0)
        self.name_entry.pack(fill="x", padx=24, pady=(0, 10))

        CTkLabel(left_card, text="Year", anchor="w").pack(fill="x", padx=24, pady=(2, 4))
        self.year_entry = CTkEntry(left_card, height=40, placeholder_text="Enter year...", fg_color="#5a5a5a", border_width=0)
        self.year_entry.pack(fill="x", padx=24, pady=(0, 10))

        CTkLabel(left_card, text="Genre", anchor="w").pack(fill="x", padx=24, pady=(2, 4))
        self.genre_entry = CTkEntry(left_card, height=40, placeholder_text="Genre tag 1, Genre tag 2", fg_color="#5a5a5a", border_width=0)
        self.genre_entry.pack(fill="x", padx=24, pady=(0, 10))

        CTkLabel(left_card, text="Actors", anchor="w").pack(fill="x", padx=24, pady=(2, 4))
        self.actors_entry = CTkEntry(left_card, height=40, placeholder_text="Enter name of actors...", fg_color="#5a5a5a", border_width=0)
        self.actors_entry.pack(fill="x", padx=24, pady=(0, 20))

        CTkLabel(right_card, text="My Comment", anchor="w").pack(fill="x", padx=24, pady=(22, 4))
        self.comment_text = CTkTextbox(right_card, height=240, fg_color="#5a5a5a", border_width=0)
        self.comment_text.pack(fill="x", padx=24, pady=(0, 14))
        self.comment_text.insert("1.0", "Type here...")
        self.comment_text.bind("<FocusIn>", self._clear_comment_placeholder)

        rating_row = CTkFrame(right_card, fg_color="transparent")
        rating_row.pack(fill="x", padx=24, pady=(6, 12))
        CTkLabel(rating_row, text="My Rating", anchor="w").pack(side="left")
        self.rating_var = StringVar(value="1")
        self.rating_menu = CTkOptionMenu(
            rating_row,
            values=["1", "2", "3", "4", "5"],
            variable=self.rating_var,
            width=90,
            fg_color="#5a5a5a",
            button_color="#5a5a5a",
            button_hover_color="#6a6a6a",
            command=self._update_rating_stars
        )
        self.rating_menu.pack(side="left", padx=(12, 10))
        self.rating_stars = CTkLabel(rating_row, text="★☆☆☆☆", font=("Arial", 24), text_color="#b8e84b")
        self.rating_stars.pack(side="left", padx=(6, 0))

        buttons_row = CTkFrame(right_card, fg_color="transparent")
        buttons_row.pack(fill="x", padx=24, pady=(16, 8))
        self.save_movie_btn = CTkButton(
            buttons_row,
            text="Save",
            command=self.add_movie,
            height=self.std_btn_height,
            fg_color="#b8e84b",
            text_color="black",
            hover_color="#c8f15f",
            font=self.std_btn_font
        )
        self.save_movie_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        CTkButton(
            buttons_row,
            text="Clear fields",
            command=self.clear_fields,
            height=self.std_btn_height,
            fg_color="#f0f0f0",
            text_color="black",
            hover_color="#ffffff",
            font=self.std_btn_font
        ).pack(side="left", fill="x", expand=True)

        self.status_label = CTkLabel(right_card, text="", font=("Arial", 13))
        self.status_label.pack(fill="x", padx=24, pady=(6, 0))
    
    def setup_movie_list_tab(self):
        """Setup home page 1:1 style layout"""
        tab = self.tab_view.tab("Movie List")
        tab.configure(fg_color="#1f1f1f")

        self._ui_images = []
        self.friend_rows = []

        page = CTkFrame(tab, fg_color="#1f1f1f")
        page.pack(fill="both", expand=True, padx=14, pady=14)

        self._build_sidebar(page, "home")

        content = CTkFrame(page, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)
        self.home_content = content
        content.grid_columnconfigure(0, weight=65)
        content.grid_columnconfigure(1, weight=0, minsize=12)
        content.grid_columnconfigure(2, weight=35)
        content.grid_rowconfigure(0, weight=1)
        self.home_content.bind("<Configure>", self._on_home_content_configure)

        left_column = CTkFrame(content, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew")
        self.home_left_column = left_column
        self.home_left_column.bind("<Configure>", self._on_home_left_column_configure)

        right_column = CTkFrame(content, fg_color="transparent")
        right_column.grid(row=0, column=2, sticky="nsew")
        self.home_right_column = right_column

        # Top bar
        top_bar = CTkFrame(left_column, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        search_wrap = CTkFrame(top_bar, fg_color="#2f2f2f", corner_radius=8, width=430, height=self.std_btn_height + 6)
        search_wrap.pack(side="left", padx=(0, 10))
        search_wrap.pack_propagate(False)
        self.search_bar = CTkEntry(search_wrap, width=360, height=34, placeholder_text="Search", fg_color="#2f2f2f", border_width=0)
        self.search_bar.pack(side="left", fill="y", padx=(10, 46), pady=0, expand=True)
        self.search_bar.bind("<KeyRelease>", self.apply_filter)
        self.search_btn = CTkButton(
            search_wrap,
            text="",
            image=self.search_icon_image,
            width=28,
            height=28,
            corner_radius=6,
            fg_color="#c5ef4d",
            text_color="black",
            hover_color="#d3f767",
            font=self.std_btn_font,
            command=self.apply_filter
        )
        self.search_btn.place(relx=1.0, rely=0.5, x=-8, anchor="e")

        self.home_filter_field = "Name"
        self.filter_buttons = {}
        filter_wrap = CTkFrame(top_bar, fg_color="transparent")
        filter_wrap.pack(side="left")
        for option in ["Name", "Genre", "Actors", "Years"]:
            btn = CTkButton(
                filter_wrap,
                text=option,
                width=86,
                height=self.std_btn_height,
                corner_radius=8,
                fg_color="#2f2f2f",
                text_color="white",
                hover_color="#3f3f3f",
                font=self.std_btn_font,
                command=lambda value=option: self._set_home_filter(value)
            )
            btn.pack(side="left", padx=(0, 6))
            self.filter_buttons[option] = btn
        self._set_home_filter("Name", refresh=False)

        # Hero and cards
        self.hero_frame = CTkFrame(left_column, fg_color="transparent", corner_radius=0, height=340)
        self.hero_frame.pack(fill="x", pady=(0, 16))
        self.hero_frame.pack_propagate(False)
        self.hero_image_label = CTkLabel(self.hero_frame, text="")
        self.hero_image_label.pack(fill="both", expand=True)
        self.hero_frame.bind("<Configure>", self._on_hero_frame_configure)

        CTkLabel(left_column, text="Popular movies", font=("Arial", 16, "bold"), anchor="w").pack(fill="x", pady=(0, 8))
        self.cards_grid = CTkFrame(left_column, fg_color="transparent")
        self.cards_grid.pack(fill="x")

        # Right column
        profile_box = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10, height=40)
        profile_box.pack(fill="x", pady=(0, 10))
        profile_box.pack_propagate(False)
        CTkLabel(profile_box, text="Movie dashboard", font=("Arial", 14, "bold")).pack(side="left", padx=12)
        CTkLabel(profile_box, text="●", text_color="#61a5ff", font=("Arial", 16, "bold")).pack(side="right", padx=12)

        CTkButton(
            right_column,
            text="+ Add new",
            height=self.std_btn_height,
            font=self.std_btn_font,
            fg_color="#c5ef4d",
            text_color="black",
            hover_color="#d3f767",
            command=lambda: self.tab_view.set("Add Movie")
        ).pack(fill="x", pady=(0, 12))

        CTkLabel(right_column, text="Currently watching", font=("Arial", 16, "bold"), anchor="w").pack(fill="x", pady=(4, 8))
        self.recent_frame = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10)
        self.recent_frame.pack(fill="both", expand=True, pady=(0, 16))

        CTkLabel(right_column, text="Movie Journal", font=("Arial", 16, "bold"), anchor="w").pack(fill="x", pady=(2, 8))
        self.journal_frame = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10)
        self.journal_frame.pack(fill="both", expand=True)
        self.journal_frame.bind("<Configure>", lambda _e: self._resize_home_journal())
        self._render_movie_journal()

        self.refresh_movie_list()
        self.after(120, self.refresh_movie_list)
        self.after(320, self.refresh_movie_list)

    def apply_filter(self, event=None):
        """Apply filter and re-render dashboard widgets"""
        self.refresh_movie_list()

    def _set_home_filter(self, selected_option, refresh=True):
        self.home_filter_field = selected_option
        if hasattr(self, "filter_buttons"):
            for option, btn in self.filter_buttons.items():
                is_selected = option == selected_option
                btn.configure(
                    fg_color="#c5ef4d" if is_selected else "#2f2f2f",
                    hover_color="#d3f767" if is_selected else "#404040",
                    text_color="black" if is_selected else "white"
                )
        if refresh:
            self.refresh_movie_list()

    def _render_movie_journal(self):
        if not hasattr(self, "journal_frame"):
            return

        for widget in self.journal_frame.winfo_children():
            widget.destroy()

        container = CTkFrame(self.journal_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        header = CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))
        CTkLabel(
            header,
            text="Write anything about movies",
            text_color="#b8e84b",
            font=("Arial", 12, "bold"),
            anchor="w"
        ).pack(side="left")

        note_box = CTkFrame(
            container,
            fg_color="#363636",
            corner_radius=10,
            border_width=1,
            border_color="#4d4d4d"
        )
        note_box.pack(fill="x", pady=(0, 8))
        self.home_journal_text = CTkTextbox(
            note_box,
            height=140,
            fg_color="#363636",
            border_width=0,
            wrap="word",
            font=("Arial", 12)
        )
        self.home_journal_text.pack(fill="x", padx=8, pady=(8, 6))
        self.home_journal_text.insert("1.0", str(self.data.get("journal_note", "")))
        self._resize_home_journal()

        actions = CTkFrame(container, fg_color="transparent")
        actions.pack(fill="x")
        self.home_journal_status = CTkLabel(
            actions,
            text="",
            text_color="#8f8f8f",
            font=("Arial", 11),
            anchor="w"
        )
        self.home_journal_status.pack(side="left", fill="x", expand=True)
        CTkButton(
            actions,
            text="Save",
            width=88,
            height=30,
            corner_radius=8,
            fg_color="#b8e84b",
            text_color="black",
            hover_color="#c8f15f",
            font=("Arial", 12, "bold"),
            command=self._save_manual_journal
        ).pack(side="right")

    def _save_manual_journal(self):
        if not hasattr(self, "home_journal_text"):
            return
        note_text = self.home_journal_text.get("1.0", "end").strip()
        self.data["journal_note"] = note_text
        self.save_data()
        if hasattr(self, "home_journal_status"):
            self.home_journal_status.configure(text="Saved", text_color="#b8e84b")
        # Move focus away so text cursor does not remain visible.
        self.focus_set()

    def _resize_home_journal(self):
        """Resize journal textbox based on available right panel height."""
        if not hasattr(self, "home_journal_text"):
            return
        journal_h = self.journal_frame.winfo_height() if hasattr(self, "journal_frame") else 0
        if journal_h > 0:
            # Keep enough room for header + status + save button + paddings.
            reserved_h = 150
            usable_h = max(95, journal_h - reserved_h)
            target_h = max(90, min(260, usable_h))
        else:
            target_h = 150
        if int(self.home_journal_text.cget("height")) != target_h:
            self.home_journal_text.configure(height=target_h)

    def setup_movies_page_tab(self):
        """Setup dedicated page for all movies in grid view."""
        tab = self.tab_view.tab("Movies Page")
        tab.configure(fg_color="#1f1f1f")

        self.movies_page_images = []
        self.movies_sort_mode = "Recently watched"
        self.movies_page_refresh_job = None

        page = CTkFrame(tab, fg_color="#1f1f1f")
        page.pack(fill="both", expand=True, padx=14, pady=14)

        # Center the whole screen content and keep stable proportions.
        shell = CTkFrame(page, fg_color="transparent")
        shell.pack(fill="both", expand=True)

        self._build_sidebar(shell, "menu")

        content_outer = CTkFrame(shell, fg_color="transparent")
        content_outer.pack(side="left", fill="both", expand=True)

        content = CTkFrame(content_outer, fg_color="transparent", width=1000)
        content.pack(expand=True, fill="both")
        content.pack_propagate(False)

        CTkLabel(content, text="My movie list", font=("Arial", 22, "bold")).pack(anchor="n", pady=(2, 12))

        self.movies_sort_segment = CTkSegmentedButton(
            content,
            values=["Recently watched", "Highest rated", "Most popular"],
            width=540,
            height=46,
            corner_radius=12,
            fg_color="#3f3f3f",
            selected_color="#b8e84b",
            selected_hover_color="#d7ff6a",
            unselected_color="#595959",
            unselected_hover_color="#6b6b6b",
            text_color="white",
            text_color_disabled="#aaaaaa",
            font=("Arial", 13, "bold"),
            command=self._set_movies_sort_mode
        )
        self.movies_sort_segment.pack(anchor="center", pady=(0, 14))
        self.movies_sort_segment.set(self.movies_sort_mode)
        self._refresh_movies_sort_segment_text()

        self.movies_scroll = CTkScrollableFrame(
            content,
            fg_color="#1f1f1f",
            corner_radius=0,
            scrollbar_button_color="#b8e84b",
            scrollbar_button_hover_color="#c8f15f",
            scrollbar_fg_color="#2a2a2a"
        )
        self.movies_scroll.pack(fill="both", expand=True, pady=(0, 2))
        self.movies_scroll.bind("<Configure>", self._schedule_movies_page_refresh)

        self.movies_grid_frame = CTkFrame(self.movies_scroll, fg_color="transparent")
        self.movies_grid_frame.pack(fill="both", expand=True)
        self.movies_grid_frame.pack_propagate(False)

        self.refresh_movies_page()
        self.after(120, self.refresh_movies_page)
        self.after(260, self.refresh_movies_page)

    def _set_movies_sort_mode(self, mode: str):
        self.movies_sort_mode = mode
        self._refresh_movies_sort_segment_text()
        self.refresh_movies_page()

    def _refresh_movies_sort_segment_text(self):
        """Ensure active sort tab uses black text."""
        if not hasattr(self, "movies_sort_segment"):
            return
        current_mode = self.movies_sort_mode
        buttons = getattr(self.movies_sort_segment, "_buttons_dict", {})
        for mode, btn in buttons.items():
            btn.configure(text_color="black" if mode == current_mode else "white")

    def _schedule_movies_page_refresh(self, event=None):
        new_width = event.width if event is not None else self.movies_scroll.winfo_width()
        if abs(new_width - self._movies_page_last_width) < 6:
            return
        if self.movies_page_refresh_job is not None:
            self.after_cancel(self.movies_page_refresh_job)
        self.movies_page_refresh_job = self.after(80, self._run_movies_page_refresh)

    def _run_movies_page_refresh(self):
        self.movies_page_refresh_job = None
        self.refresh_movies_page()

    def _movie_rating_value(self, movie):
        try:
            return int(str(movie.get("rating", "0")))
        except ValueError:
            return 0

    def _sorted_movies_for_page(self):
        movies = list(self.data.get("movies", []))
        mode = self.movies_sort_mode
        if mode == "Highest rated":
            movies.sort(key=lambda m: self._movie_rating_value(m), reverse=True)
        elif mode == "Most popular":
            movies.sort(key=lambda m: len(str(m.get("comment", "")).strip()), reverse=True)
        else:
            movies = movies[::-1]
        return movies

    def refresh_movies_page(self):
        """Refresh dedicated movies page grid cards."""
        if not hasattr(self, "movies_scroll"):
            return

        # Avoid re-layout too early (width can be 1 right after tab switch).
        viewport_w = self.movies_scroll.winfo_width()
        if viewport_w < 500:
            self.after(120, self.refresh_movies_page)
            return

        movies = self._sorted_movies_for_page()
        signature = (
            self.movies_sort_mode,
            viewport_w // 6,
            tuple(
                (
                    str(m.get("title", "")),
                    str(m.get("year", "")),
                    str(m.get("image", "")),
                    str(m.get("rating", "")),
                    str(m.get("genre", "")),
                )
                for m in movies
            ),
        )
        if signature == self._movies_page_last_signature:
            return
        self._movies_page_last_signature = signature
        self._movies_page_last_width = viewport_w

        self.movies_page_images = []
        for widget in self.movies_grid_frame.winfo_children():
            widget.destroy()

        if not movies:
            empty = CTkLabel(self.movies_grid_frame, text="No movies yet. Add your first one from Add Movie.", text_color="lightgray", anchor="center")
            empty.pack(fill="both", expand=True)
            return

        # Modern responsive card layout.
        card_w = 245
        card_h = 250
        h_gap = 18
        v_gap = 18

        usable_w = max(0, viewport_w - 24)
        max_cols = max(1, int((usable_w + h_gap) // (card_w + h_gap)))
        cols = min(max(1, max_cols), 5)

        # Center each row by computing left margin.
        row_w = cols * card_w + (cols - 1) * h_gap
        left_margin = max(0, int((usable_w - row_w) / 2))

        for idx, movie in enumerate(movies):
            row = idx // cols
            col = idx % cols

            x = left_margin + col * (card_w + h_gap)
            y = 0 + row * (card_h + v_gap)

            card = CTkFrame(
                self.movies_grid_frame,
                fg_color="#2f2f2f",
                corner_radius=14,
                width=card_w,
                height=card_h,
                border_width=1,
                border_color="#454545"
            )
            card.place(x=x, y=y)
            card.pack_propagate(False)

            poster_path = self._resolve_image_path(movie)
            poster_img = self._make_image_cover_rounded(poster_path, (card_w - 20, 126), radius=12)

            if poster_img:
                self.movies_page_images.append(poster_img)
                poster_label = CTkLabel(card, image=poster_img, text="")
            else:
                poster_label = CTkLabel(card, text="No image", width=card_w - 20, height=126, fg_color="#444444", corner_radius=10)

            poster_label.pack(padx=10, pady=(10, 8))
            poster_label.bind("<Button-1>", lambda _e, m=movie: self.open_movie_details(m))
            poster_label.configure(cursor="hand2")

            title = str(movie.get("title", "Unknown"))
            genre = str(movie.get("genre", ""))
            rating = self._movie_rating_value(movie)
            stars = "★" * max(0, min(5, rating))

            info_top = CTkFrame(card, fg_color="transparent")
            info_top.pack(fill="x", padx=10, pady=(0, 4))
            CTkLabel(info_top, text=title, anchor="w", font=("Arial", 14, "bold")).pack(side="left")
            CTkLabel(info_top, text=f"{stars}", anchor="e", text_color="#b8e84b", font=("Arial", 13, "bold")).pack(side="right")

            CTkLabel(card, text=genre, anchor="w", text_color="#a8a8a8", font=("Arial", 11)).pack(fill="x", padx=10)

            action_row = CTkFrame(card, fg_color="transparent", height=54)
            action_row.pack(side="bottom", fill="x", padx=10, pady=(8, 10))
            action_row.pack_propagate(False)

            CTkButton(
                action_row,
                text="Details",
                height=40,
                fg_color="#b8e84b",
                text_color="black",
                hover_color="#c8f15f",
                font=("Arial", 13, "bold"),
                command=lambda m=movie: self.open_movie_details(m)
            ).pack(fill="both", expand=True)

        total_rows = (len(movies) + cols - 1) // cols
        total_h = total_rows * (card_h + v_gap)
        self.movies_grid_frame.configure(height=total_h)

    def setup_movie_details_tab(self):
        """Setup single movie details page."""
        tab = self.tab_view.tab("Movie Details")
        tab.configure(fg_color="#1f1f1f")

        self.current_detail_movie = None

        page = CTkFrame(tab, fg_color="#1f1f1f")
        page.pack(fill="both", expand=True, padx=14, pady=14)

        shell = CTkFrame(page, fg_color="transparent")
        shell.pack(fill="both", expand=True)

        self._build_sidebar(shell, "menu")

        content_outer = CTkFrame(shell, fg_color="transparent")
        content_outer.pack(side="left", fill="both", expand=True)

        content = CTkFrame(content_outer, fg_color="transparent")
        content.pack(expand=True, fill="both")

        CTkLabel(content, text="Details", font=("Arial", 22, "bold")).pack(anchor="n", pady=(2, 10))

        body = CTkFrame(content, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=65)
        body.grid_columnconfigure(1, weight=0, minsize=28)
        body.grid_columnconfigure(2, weight=35)
        body.grid_rowconfigure(0, weight=1)
        self.details_body = body
        self.details_body.bind("<Configure>", self._on_details_body_configure)

        left_col = CTkFrame(body, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew")
        self.details_left_col = left_col
        self.details_left_col.bind("<Configure>", self._on_details_left_col_configure)
        left_col.grid_propagate(False)

        right_col = CTkFrame(body, fg_color="transparent")
        right_col.grid(row=0, column=2, sticky="nsew")
        right_col.grid_propagate(False)

        self.details_poster_box = CTkFrame(left_col, fg_color="#2f2f2f", corner_radius=12, height=330)
        self.details_poster_box.pack(fill="x", pady=(0, 10))
        self.details_poster_box.pack_propagate(False)
        self.details_poster_label = CTkLabel(self.details_poster_box, text="")
        self.details_poster_label.pack(fill="both", expand=True, padx=6, pady=6)
        self.details_poster_box.bind("<Configure>", lambda _e: self.refresh_movie_details())

        self.details_title_label = CTkLabel(left_col, text="No movie selected", anchor="w", font=("Arial", 18, "bold"))
        self.details_title_label.pack(fill="x", pady=(0, 2))
        CTkLabel(left_col, text="My comment", anchor="w", text_color="#b8e84b", font=("Arial", 16, "bold")).pack(fill="x", pady=(0, 4))
        self.details_comment_box = CTkTextbox(
            left_col,
            fg_color="#1f1f1f",
            border_width=0,
            text_color="#d8d8d8",
            font=("Arial", 13),
            wrap="word"
        )
        self.details_comment_box.pack(fill="both", expand=True)
        self.details_comment_box.insert("1.0", "Open a movie details card to preview full information.")
        self.details_comment_box.configure(state="disabled")

        CTkLabel(right_col, text="My Rating", anchor="w", text_color="#b8e84b", font=("Arial", 16, "bold")).pack(fill="x", pady=(10, 2))
        self.details_rating_label = CTkLabel(right_col, text="☆☆☆☆☆", anchor="w", text_color="#b8e84b", font=("Arial", 30, "bold"))
        self.details_rating_label.pack(fill="x", pady=(0, 10))

        self.details_year_label = CTkLabel(right_col, text="Year: -", anchor="w", justify="left", wraplength=410, font=("Arial", 14, "bold"))
        self.details_year_label.pack(fill="x", pady=(0, 8))
        self.details_actors_label = CTkLabel(right_col, text="Actors: -", justify="left", wraplength=410, anchor="w", font=("Arial", 14, "bold"))
        self.details_actors_label.pack(fill="x", pady=(0, 8))
        self.details_genre_label = CTkLabel(right_col, text="Genre: -", justify="left", wraplength=410, anchor="w", font=("Arial", 14, "bold"))
        self.details_genre_label.pack(fill="x", pady=(0, 14))

        CTkLabel(right_col, text="Currently watching", anchor="w", font=("Arial", 16, "bold")).pack(fill="x", pady=(8, 8))
        self.details_watch_frame = CTkFrame(right_col, fg_color="#2f2f2f", corner_radius=10)
        self.details_watch_frame.pack(fill="x")

        details_actions = CTkFrame(right_col, fg_color="transparent")
        details_actions.pack(fill="x", pady=(12, 0))
        CTkButton(
            details_actions,
            text="Edit",
            height=self.std_btn_height,
            fg_color="#b8e84b",
            text_color="black",
            hover_color="#c8f15f",
            font=self.std_btn_font,
            command=self.edit_current_movie
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        CTkButton(
            details_actions,
            text="Delete",
            height=self.std_btn_height,
            fg_color="#c14f4f",
            text_color="white",
            hover_color="#d25f5f",
            font=self.std_btn_font,
            command=self.delete_current_movie
        ).pack(side="left", fill="x", expand=True)

        self.refresh_movie_details()

    def open_movie_details(self, movie):
        """Open the Movie Details tab for selected movie."""
        self.current_detail_movie = movie
        self.refresh_movie_details()
        self.tab_view.set("Movie Details")

    def refresh_movie_details(self):
        """Refresh movie details page widgets."""
        if not hasattr(self, "details_title_label"):
            return

        movie = self.current_detail_movie
        self._ui_images = []

        if not movie:
            self.details_poster_label.configure(image=None, text="No image")
            self.details_title_label.configure(text="No movie selected")
            self.details_comment_box.configure(state="normal")
            self.details_comment_box.delete("1.0", END)
            self.details_comment_box.insert("1.0", "Open a movie details card to preview full information.")
            self.details_comment_box.configure(state="disabled")
            self.details_rating_label.configure(text="☆☆☆☆☆")
            self.details_year_label.configure(text="Year: -")
            self.details_actors_label.configure(text="Actors: -")
            self.details_genre_label.configure(text="Genre: -")
        else:
            title = str(movie.get("title", "Unknown"))
            year = str(movie.get("year", "-"))
            actors = self._normalize_actors(movie.get("actors", "-"))
            genre = str(movie.get("genre", "-"))
            comment = str(movie.get("comment", "")).strip() or "No comment yet."
            rating = self._movie_rating_value(movie)
            stars = "★" * max(0, min(5, rating)) + "☆" * (5 - max(0, min(5, rating)))

            poster_path = self._resolve_image_path(movie)
            poster_w = max(self.details_poster_box.winfo_width() - 12, 240)
            poster_h = max(self.details_poster_box.winfo_height() - 12, 140)
            adaptive_radius = max(12, min(34, int(min(poster_w, poster_h) * 0.09)))
            render_key = (id(movie), poster_w, poster_h, adaptive_radius)
            if render_key == self._details_last_render_key:
                poster_img = None
            else:
                self._details_last_render_key = render_key
                poster_img = self._make_image_cover_rounded(
                    poster_path,
                    (poster_w, poster_h),
                    radius=adaptive_radius
                )
            if poster_img:
                self.details_poster_label.configure(image=poster_img, text="")
            elif self.details_poster_label.cget("image"):
                # Keep existing image when size didn't change.
                pass
            else:
                self.details_poster_label.configure(image=None, text="No image")

            self.details_title_label.configure(text=title)
            self.details_comment_box.configure(state="normal")
            self.details_comment_box.delete("1.0", END)
            self.details_comment_box.insert("1.0", comment)
            self.details_comment_box.configure(state="disabled")
            self.details_rating_label.configure(text=stars)
            self.details_year_label.configure(text=f"Year: {year}", text_color="#dcdcdc")
            self.details_actors_label.configure(text=f"Actors: {actors}", text_color="#dcdcdc")
            self.details_genre_label.configure(text=f"Genre: {genre}", text_color="#dcdcdc")

        for widget in self.details_watch_frame.winfo_children():
            widget.destroy()

        movies = list(self.data.get("movies", []))[::-1]
        if movie:
            movies = [m for m in movies if m is not movie]
        movies = movies[:3]
        for watch_movie in movies:
            row = CTkFrame(self.details_watch_frame, fg_color="#3a3a3a", corner_radius=8, height=84)
            row.pack(fill="x", padx=8, pady=6)
            row.pack_propagate(False)
            row_inner = CTkFrame(row, fg_color="transparent")
            row_inner.pack(fill="x", padx=6, pady=6)
            row_inner.grid_columnconfigure(0, weight=0)
            row_inner.grid_columnconfigure(1, weight=1)
            row_inner.grid_columnconfigure(2, weight=0)

            thumb_path = self._resolve_image_path(watch_movie)
            thumb_img = self._make_image_cover_rounded(thumb_path, (110, 62), radius=8)
            if thumb_img:
                CTkLabel(row_inner, image=thumb_img, text="").grid(row=0, column=0, rowspan=2, padx=(0, 8), sticky="w")
            else:
                CTkLabel(row_inner, text="No image", width=110, height=62, fg_color="#4a4a4a", corner_radius=8).grid(row=0, column=0, rowspan=2, padx=(0, 8), sticky="w")

            title = str(watch_movie.get("title", "Untitled"))
            year = str(watch_movie.get("year", ""))
            CTkLabel(row_inner, text=f"{title}  •  {year}", anchor="w", font=("Arial", 13, "bold")).grid(row=0, column=1, sticky="w", pady=(2, 0))
            CTkLabel(row_inner, text=str(watch_movie.get("genre", "")), anchor="w", text_color="#c9c9c9", font=("Arial", 11)).grid(row=1, column=1, sticky="w")
            CTkButton(
                row_inner,
                text="Open",
                width=70,
                height=self.std_btn_height,
                fg_color="#b8e84b",
                text_color="black",
                hover_color="#c8f15f",
                font=self.std_btn_font,
                command=lambda m=watch_movie: self.open_movie_details(m)
            ).grid(row=0, column=2, rowspan=2, padx=(8, 0), sticky="e")

    def _on_details_left_col_configure(self, event=None):
        """Keep details page responsive and wrapped comment text."""
        if not hasattr(self, "details_left_col") or not hasattr(self, "details_poster_box"):
            return

        col_w = self.details_left_col.winfo_width()
        col_h = self.details_left_col.winfo_height()
        if col_w <= 0 or col_h <= 0:
            return

        # Adaptive poster height for balanced fullscreen layout.
        target_h = max(280, min(440, int(col_h * 0.45)))
        if self.details_poster_box.cget("height") != target_h:
            self.details_poster_box.configure(height=target_h)

        if hasattr(self, "details_comment_box"):
            self.details_comment_box.configure(width=max(320, col_w - 24))

    def _on_details_body_configure(self, event=None):
        """Enforce exact 65/35 visual split for details columns."""
        if not hasattr(self, "details_body"):
            return
        body_w = self.details_body.winfo_width()
        if body_w <= 0:
            return
        gap = 28
        usable_w = max(0, body_w - gap)
        left_w = int(usable_w * 0.65)
        right_w = usable_w - left_w
        self.details_body.grid_columnconfigure(0, minsize=left_w)
        self.details_body.grid_columnconfigure(2, minsize=right_w)

    def _run_details_resize_refresh(self):
        self._details_resize_job = None
        self.refresh_movie_details()


    def _normalize_actors(self, actors_value):
        if isinstance(actors_value, list):
            return ", ".join(actors_value)
        return str(actors_value or "")

    def _resolve_image_path(self, movie):
        image_rel_path = str(movie.get("image", "")).strip()
        if image_rel_path:
            normalized_rel = image_rel_path.replace("\\", os.sep).replace("/", os.sep)
            abs_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), normalized_rel))
            if os.path.exists(abs_path):
                return abs_path
        return None

    def _make_image(self, image_path, size):
        if not image_path:
            return None
        try:
            mtime = os.path.getmtime(image_path)
            cache_key = ("plain", image_path, size[0], size[1], int(mtime))
            cached = self._ctk_image_cache.get(cache_key)
            if cached is not None:
                return cached

            img = Image.open(image_path).convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)
            ctk_img = CTkImage(light_image=img, dark_image=img, size=size)
            self._ctk_image_cache[cache_key] = ctk_img
            self._ui_images.append(ctk_img)
            return ctk_img
        except Exception:
            return None

    def _create_icon_from_png(self, png_path, size=16):
        """Load icon directly from PNG file."""
        try:
            img = Image.open(png_path).convert("RGBA")
            return CTkImage(light_image=img, dark_image=img, size=(size, size))
        except Exception:
            return None

    def _make_image_cover(self, image_path, size):
        """Create image in cover mode: fill area without distortion."""
        if not image_path:
            return None
        try:
            target_w, target_h = size
            mtime = os.path.getmtime(image_path)
            cache_key = ("cover", image_path, target_w, target_h, int(mtime))
            cached = self._ctk_image_cache.get(cache_key)
            if cached is not None:
                return cached

            img = Image.open(image_path).convert("RGBA")
            src_w, src_h = img.size

            if src_w == 0 or src_h == 0:
                return None

            src_ratio = src_w / src_h
            target_ratio = target_w / target_h

            if src_ratio > target_ratio:
                # Source is wider: crop left/right
                new_w = int(src_h * target_ratio)
                left = (src_w - new_w) // 2
                img = img.crop((left, 0, left + new_w, src_h))
            else:
                # Source is taller: crop top/bottom
                new_h = int(src_w / target_ratio)
                top = (src_h - new_h) // 2
                img = img.crop((0, top, src_w, top + new_h))

            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
            self._ctk_image_cache[cache_key] = ctk_img
            self._ui_images.append(ctk_img)
            return ctk_img
        except Exception:
            return None

    def _make_image_cover_rounded(self, image_path, size, radius=10):
        """Create cover image with rounded corners."""
        if not image_path:
            return None
        try:
            target_w, target_h = size
            mtime = os.path.getmtime(image_path)
            cache_key = ("cover_rounded", image_path, target_w, target_h, radius, int(mtime))
            cached = self._ctk_image_cache.get(cache_key)
            if cached is not None:
                return cached

            img = Image.open(image_path).convert("RGBA")
            src_w, src_h = img.size

            if src_w == 0 or src_h == 0:
                return None

            src_ratio = src_w / src_h
            target_ratio = target_w / target_h

            if src_ratio > target_ratio:
                new_w = int(src_h * target_ratio)
                left = (src_w - new_w) // 2
                img = img.crop((left, 0, left + new_w, src_h))
            else:
                new_h = int(src_w / target_ratio)
                top = (src_h - new_h) // 2
                img = img.crop((0, top, src_w, top + new_h))

            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Build anti-aliased rounded mask (supersampling) to avoid jagged corners.
            scale = 4
            mask_large = Image.new("L", (target_w * scale, target_h * scale), 0)
            draw_large = ImageDraw.Draw(mask_large)
            draw_large.rounded_rectangle(
                (0, 0, target_w * scale - 1, target_h * scale - 1),
                radius=radius * scale,
                fill=255
            )
            mask = mask_large.resize((target_w, target_h), Image.Resampling.LANCZOS)
            img.putalpha(mask)

            ctk_img = CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
            self._ctk_image_cache[cache_key] = ctk_img
            self._ui_images.append(ctk_img)
            return ctk_img
        except Exception:
            return None

    def _make_image_contain_rounded(self, image_path, size, radius=10, bg_color=(47, 47, 47, 255)):
        """Create contain image with rounded corners (shows full image)."""
        if not image_path:
            return None
        try:
            target_w, target_h = size
            mtime = os.path.getmtime(image_path)
            cache_key = ("contain_rounded", image_path, target_w, target_h, radius, bg_color, int(mtime))
            cached = self._ctk_image_cache.get(cache_key)
            if cached is not None:
                return cached

            source = Image.open(image_path).convert("RGBA")
            source.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)

            canvas = Image.new("RGBA", (target_w, target_h), bg_color)
            offset_x = (target_w - source.width) // 2
            offset_y = (target_h - source.height) // 2
            canvas.paste(source, (offset_x, offset_y), source)

            scale = 4
            mask_large = Image.new("L", (target_w * scale, target_h * scale), 0)
            draw_large = ImageDraw.Draw(mask_large)
            draw_large.rounded_rectangle(
                (0, 0, target_w * scale - 1, target_h * scale - 1),
                radius=radius * scale,
                fill=255
            )
            mask = mask_large.resize((target_w, target_h), Image.Resampling.LANCZOS)
            canvas.putalpha(mask)

            ctk_img = CTkImage(light_image=canvas, dark_image=canvas, size=(target_w, target_h))
            self._ctk_image_cache[cache_key] = ctk_img
            self._ui_images.append(ctk_img)
            return ctk_img
        except Exception:
            return None

    def _get_filtered_movies(self):
        filter_text = self.search_bar.get().strip().lower()
        field = getattr(self, "home_filter_field", "Name")
        results = []
        for movie in self.data.get("movies", []):
            title = str(movie.get("title", "")).lower()
            genre = str(movie.get("genre", "")).lower()
            actors = self._normalize_actors(movie.get("actors", "")).lower()
            year = str(movie.get("year", "")).lower()

            if not filter_text:
                results.append(movie)
                continue

            match = False
            if field == "Name":
                match = filter_text in title
            elif field == "Genre":
                match = filter_text in genre
            elif field == "Actors":
                match = filter_text in actors
            elif field == "Years":
                match = filter_text in year

            if match:
                results.append(movie)
        return results

    def _movies_with_posters(self, movies):
        poster_movies = []
        for movie in movies:
            if str(movie.get("image", "")).strip():
                path = self._resolve_image_path(movie)
                if path and os.path.exists(path):
                    poster_movies.append(movie)
        return poster_movies

    def _on_hero_frame_configure(self, event=None):
        self._render_hero_image()

    def _on_home_left_column_configure(self, event=None):
        """Scale hero box height with available space (better fullscreen look)."""
        if not hasattr(self, "hero_frame") or not hasattr(self, "home_left_column"):
            return
        column_h = self.home_left_column.winfo_height()
        if column_h <= 0:
            return
        column_w = self.home_left_column.winfo_width()
        # More adaptive hero height on large/fullscreen windows.
        height_by_screen = int(column_h * 0.56)
        height_by_width = int(column_w * 0.44) if column_w > 0 else 0
        target_h = max(320, min(620, max(height_by_screen, height_by_width)))
        if self.hero_frame.cget("height") != target_h:
            self.hero_frame.configure(height=target_h)

        if hasattr(self, "cards_grid"):
            cards_w = self.cards_grid.winfo_width()
            if cards_w > 0 and abs(cards_w - self._home_cards_last_width) >= 18:
                self._home_cards_last_width = cards_w
                if self._home_cards_resize_job:
                    self.after_cancel(self._home_cards_resize_job)
                if self._home_cards_settle_job:
                    self.after_cancel(self._home_cards_settle_job)
                # Two-phase refresh: quick + settle for instant fullscreen transitions.
                self._home_cards_resize_job = self.after(90, lambda: self.refresh_movie_list(reason="resize"))
                self._home_cards_settle_job = self.after(260, lambda: self.refresh_movie_list(reason="resize"))

    def _on_home_content_configure(self, event=None):
        """Keep homepage columns fixed so cards can't push the right panel."""
        if not hasattr(self, "home_content"):
            return
        content_w = self.home_content.winfo_width()
        if content_w <= 0:
            return
        gap = 12
        usable_w = max(0, content_w - gap)
        left_w = int(usable_w * 0.65)
        right_w = usable_w - left_w
        self.home_content.grid_columnconfigure(0, minsize=left_w)
        self.home_content.grid_columnconfigure(2, minsize=right_w)
        if hasattr(self, "recent_frame"):
            self.after_idle(lambda: self.refresh_movie_list(reason="resize"))
        if hasattr(self, "home_journal_text"):
            self.after_idle(self._resize_home_journal)

    def _render_hero_image(self):
        if not hasattr(self, "hero_frame") or not hasattr(self, "hero_image_label"):
            return

        hero_movie = getattr(self, "current_hero_movie", None)
        hero_path = self._resolve_image_path(hero_movie) if hero_movie else None
        if not hero_path:
            self.hero_image_label.configure(image=None, text="No image")
            return

        hero_w = self.hero_frame.winfo_width() - 4
        hero_h = self.hero_frame.winfo_height() - 4
        if hero_w < 120 or hero_h < 80:
            return

        adaptive_radius = max(10, min(24, int(min(hero_w, hero_h) * 0.05)))
        hero_img = self._make_image_cover_rounded(hero_path, (hero_w, hero_h), radius=adaptive_radius)
        if hero_img:
            self.hero_image_label.configure(image=hero_img, text="")
        else:
            self.hero_image_label.configure(image=None, text="No image")

    def refresh_movie_list(self, reason="data"):
        """Refresh all dashboard areas"""
        filtered_movies = self._get_filtered_movies()
        self._ui_images = []
        all_movies = self.data.get("movies", [])
        latest_filtered_movies = list(reversed(filtered_movies))
        latest_all_movies = list(reversed(all_movies))

        # Hero image
        self.current_hero_movie = latest_filtered_movies[0] if latest_filtered_movies else (latest_all_movies[0] if latest_all_movies else None)
        self.after_idle(self._render_hero_image)

        # Cards
        card_pool = latest_filtered_movies if latest_filtered_movies else latest_all_movies
        card_movies = []
        cards_area_w = 0
        target_cards = 3
        card_w = 245
        card_gap = 12
        if card_pool:
            cards_area_w = self.cards_grid.winfo_width()
            if cards_area_w <= 0 and hasattr(self, "home_left_column"):
                cards_area_w = max(0, self.home_left_column.winfo_width() - 8)
            # Prefer stretching existing cards; add a new card only when needed.
            max_card_w = 300
            fit_count = max(1, int((cards_area_w + card_gap + (max_card_w + card_gap) - 1) // (max_card_w + card_gap)))
            target_cards = max(3, fit_count)
            if cards_area_w > 0:
                # Fluid width: cards expand/shrink to fill the whole row.
                card_w = int((cards_area_w - (card_gap * (target_cards - 1))) / target_cards)
                card_w = max(210, min(300, card_w))
            idx = 0
            while len(card_movies) < target_cards:
                card_movies.append(card_pool[idx % len(card_pool)])
                idx += 1

        card_key = (
            target_cards,
            card_w,
            tuple(str(m.get("title", "")) for m in card_movies),
            tuple(str(m.get("image", "")) for m in card_movies),
        )
        if card_key != self._home_cards_last_render_key:
            self._home_cards_last_render_key = card_key
            for widget in self.cards_grid.winfo_children():
                widget.destroy()

            if not card_movies:
                CTkLabel(self.cards_grid, text="No movies found for this filter.", text_color="lightgray").pack(anchor="w")
            else:
                poster_w = max(170, card_w - 20)
                poster_h = max(126, int(poster_w * 0.58))
                card_h = max(252, poster_h + 126)

                for idx, movie in enumerate(card_movies):
                    card = CTkFrame(
                        self.cards_grid,
                        fg_color="#2f2f2f",
                        corner_radius=14,
                        width=card_w,
                        height=card_h,
                        border_width=1,
                        border_color="#454545"
                    )
                    right_gap = card_gap if idx < len(card_movies) - 1 else 0
                    card.pack(side="left", fill="y", padx=(0, right_gap), pady=(0, 10))
                    card.pack_propagate(False)

                    poster_path = self._resolve_image_path(movie)
                    poster_img = self._make_image_cover_rounded(poster_path, (poster_w, poster_h), radius=12)
                    if poster_img:
                        poster_label = CTkLabel(card, image=poster_img, text="")
                    else:
                        poster_label = CTkLabel(card, text="No image", width=poster_w, height=poster_h, fg_color="#444444", corner_radius=10)
                    poster_label.pack(pady=(8, 6), padx=8)
                    poster_label.bind("<Button-1>", lambda _e, m=movie: self.open_movie_details(m))
                    poster_label.configure(cursor="hand2")

                    CTkLabel(card, text=str(movie.get("title", "Unknown")), font=("Arial", 16, "bold"), anchor="w").pack(fill="x", padx=10)
                    info_row = CTkFrame(card, fg_color="transparent")
                    info_row.pack(fill="x", padx=10, pady=(0, 6))
                    CTkLabel(info_row, text=str(movie.get("genre", "")), text_color="#bdbdbd", anchor="w", font=("Arial", 12)).pack(side="left")
                    rating = self._movie_rating_value(movie)
                    CTkLabel(info_row, text=f"{rating} ★" if rating else "☆", text_color="#b8e84b", anchor="e", font=("Arial", 12, "bold")).pack(side="right")
                    action_row = CTkFrame(card, fg_color="transparent", height=54)
                    action_row.pack(side="bottom", fill="x", padx=10, pady=(8, 10))
                    action_row.pack_propagate(False)
                    CTkButton(
                        action_row,
                        text="Details",
                        height=40,
                        fg_color="#b8e84b",
                        text_color="black",
                        hover_color="#c8f15f",
                        font=("Arial", 13, "bold"),
                        command=lambda m=movie: self.open_movie_details(m)
                    ).pack(fill="both", expand=True)

        # Recently added
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
        watching_source = latest_all_movies
        watching_movies = watching_source[:3]
        if watching_movies:
            while len(watching_movies) < 3:
                watching_movies.append(watching_movies[-1])

        frame_w = max(280, self.recent_frame.winfo_width())
        thumb_w = max(100, min(150, int(frame_w * 0.32)))
        thumb_h = int(thumb_w * 0.56)
        title_font = max(14, min(17, int(frame_w * 0.045)))
        genre_font = max(11, min(13, int(frame_w * 0.035)))

        recent_content = CTkFrame(self.recent_frame, fg_color="transparent")
        recent_content.pack(fill="both", expand=True, padx=4, pady=4)
        CTkFrame(recent_content, fg_color="transparent", height=1).pack(fill="x", expand=True)

        for movie in watching_movies:
            title = str(movie.get("title", "Untitled"))
            year = str(movie.get("year", ""))
            row = CTkFrame(recent_content, fg_color="#3a3a3a", corner_radius=8)
            row.pack(fill="x", padx=10, pady=7)
            row_inner = CTkFrame(row, fg_color="transparent")
            row_inner.pack(fill="both", expand=True, padx=8, pady=8)
            thumb_path = self._resolve_image_path(movie)
            thumb_img = self._make_image_cover_rounded(thumb_path, (thumb_w, thumb_h), radius=8)
            if thumb_img:
                CTkLabel(row_inner, image=thumb_img, text="").pack(side="left", padx=(0, 10))
            meta = CTkFrame(row_inner, fg_color="transparent")
            meta.pack(side="left", fill="both", expand=True)
            CTkLabel(meta, text=f"{title} • {year}", anchor="w", font=("Arial", title_font, "bold")).pack(fill="x", pady=(2, 1))
            CTkLabel(meta, text=str(movie.get("genre", "")), anchor="w", text_color="lightgray", font=("Arial", genre_font)).pack(fill="x")
        CTkFrame(recent_content, fg_color="transparent", height=1).pack(fill="x", expand=True)

        if reason != "resize":
            self._render_movie_journal()
    
    
    def add_movie(self):
        """Add a new movie to the collection"""
        # Get values from entries
        name = self.name_entry.get().strip()
        genre = self.genre_entry.get().strip()
        actors = self.actors_entry.get().strip()
        year = self.year_entry.get().strip()

        error_message = self._validate_add_movie_input(name, genre, actors, year, self.selected_image_path)
        if error_message:
            self.status_label.configure(text=error_message, text_color="#ff6b6b")
            return

        # Handle image
        image_path_value = ""
        if self.selected_image_path:
            try:
                filename = os.path.basename(self.selected_image_path)
                target_path = os.path.join(self.images_dir, filename)

                if not os.path.exists(target_path):
                    shutil.copy2(self.selected_image_path, target_path)

                # Save relative path to project folder
                base_dir = os.path.dirname(os.path.abspath(__file__))
                image_path_value = os.path.relpath(target_path, start=base_dir)
            except Exception:
                image_path_value = ""
        
        # Create movie dictionary
        comment_text = ""
        if hasattr(self, "comment_text"):
            comment_text = self.comment_text.get("1.0", "end").strip()
            if comment_text == "Type here...":
                comment_text = ""

        existing_image = ""
        if self.edit_movie_index is not None and 0 <= self.edit_movie_index < len(self.data.get("movies", [])):
            existing_image = str(self.data["movies"][self.edit_movie_index].get("image", ""))

        movie = {
            "title": name,
            "genre": genre,
            "actors": actors,
            "year": year,
            "image": image_path_value if image_path_value else existing_image,
            "comment": comment_text,
            "rating": self.rating_var.get() if hasattr(self, "rating_var") else "1"
        }
        
        # Add/update data and save
        if self.edit_movie_index is not None and 0 <= self.edit_movie_index < len(self.data.get("movies", [])):
            self.data["movies"][self.edit_movie_index] = movie
            action_text = "updated"
        else:
            self.data["movies"].append(movie)
            action_text = "added"
        self.save_data()
        
        # Show success message
        self.status_label.configure(text=f"✓ '{name}' {action_text} successfully!", text_color="green")
        self.edit_movie_index = None
        if hasattr(self, "save_movie_btn"):
            self.save_movie_btn.configure(text="Save")
        
        # Clear fields
        self.clear_fields()
        
        # Refresh the movie list tab
        self.refresh_movie_list()
        self.refresh_movies_page()

    def _validate_add_movie_input(self, name, genre, actors, year, selected_image_path):
        """Validate user input for Add Movie form."""
        current_year = datetime.now().year

        if not name:
            return "Movie title is required."
        if len(name) < 2:
            return "Movie title must be at least 2 characters."

        if not year:
            return "Year is required."
        if not year.isdigit():
            return "Year must contain only numbers."
        year_value = int(year)
        if year_value < 1888 or year_value > current_year + 2:
            return f"Year must be between 1888 and {current_year + 2}."

        if not genre:
            return "Genre is required."
        if len(genre) < 2:
            return "Genre must be at least 2 characters."

        if not actors:
            return "Actors field is required."
        if len(actors) < 2:
            return "Actors must be at least 2 characters."

        if not selected_image_path:
            return "Movie poster image is required."

        if hasattr(self, "rating_var"):
            rating_value = str(self.rating_var.get()).strip()
            if rating_value not in {"1", "2", "3", "4", "5"}:
                return "Rating must be between 1 and 5."

        return None
    
    def clear_fields(self):
        """Clear all input fields"""
        self.name_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.actors_entry.delete(0, END)
        self.year_entry.delete(0, END)
        self.selected_image_path = None
        if hasattr(self, "image_label"):
            self.image_label.configure(text="No image selected", text_color="lightgray")
        if hasattr(self, "comment_text"):
            self.comment_text.delete("1.0", END)
            self.comment_text.insert("1.0", "Type here...")
        if hasattr(self, "rating_var"):
            self.rating_var.set("1")
            self._update_rating_stars("1")
        self.edit_movie_index = None
        if hasattr(self, "save_movie_btn"):
            self.save_movie_btn.configure(text="Save")

    def choose_image(self):
        """Open file dialog to choose an image for the movie"""
        file_path = filedialog.askopenfilename(
            title="Choose movie image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp *.gif"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.selected_image_path = file_path
            filename = os.path.basename(file_path)
            self.image_label.configure(text=filename, text_color="white")

    def _on_add_left_card_configure(self, event=None):
        """Scale upload area height with available space on Add page."""
        if not hasattr(self, "upload_canvas") or not hasattr(self, "add_left_card"):
            return
        card_h = self.add_left_card.winfo_height()
        if card_h <= 0:
            return
        target_h = max(126, min(190, int(card_h * 0.24)))
        if int(self.upload_canvas.cget("height")) != target_h:
            self.upload_canvas.configure(height=target_h)
            self._draw_upload_placeholder()

    def _draw_upload_placeholder(self, event=None):
        """Draw rounded dashed border + centered upload text."""
        if not hasattr(self, "upload_canvas"):
            return
        canvas = self.upload_canvas
        canvas.configure(bg=self.upload_bg_color if hasattr(self, "upload_bg_color") else "#545454")
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 30 or h < 30:
            return

        pad = 8
        r = 16
        x1, y1 = pad, pad
        x2, y2 = w - pad, h - pad
        border_color = self.upload_border_color if hasattr(self, "upload_border_color") else "#b8e84b"
        border_width = 1
        dash = (10, 8)

        # Rounded dashed border built from lines + arcs.
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=border_color, width=border_width, dash=dash)
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=border_color, width=border_width, dash=dash)
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=border_color, width=border_width, dash=dash)
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=border_color, width=border_width, dash=dash)
        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style="arc", outline=border_color, width=border_width)
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style="arc", outline=border_color, width=border_width)
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style="arc", outline=border_color, width=border_width)
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style="arc", outline=border_color, width=border_width)
        canvas.create_text(
            w / 2,
            h / 2 - 10,
            text="+",
            fill="#b8e84b",
            font=("Arial", 22, "bold")
        )
        canvas.create_text(
            w / 2,
            h / 2 + 14,
            text="Upload poster",
            fill="#b8e84b",
            font=("Arial", 13, "bold")
        )

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb_color):
        return "#{:02x}{:02x}{:02x}".format(*rgb_color)

    def _animate_upload_hover(self, target_border_color, target_bg_color):
        if not hasattr(self, "upload_canvas"):
            return
        if self.upload_hover_job:
            self.after_cancel(self.upload_hover_job)
            self.upload_hover_job = None

        start_border = self._hex_to_rgb(self.upload_border_color)
        end_border = self._hex_to_rgb(target_border_color)
        start_bg = self._hex_to_rgb(self.upload_bg_color)
        end_bg = self._hex_to_rgb(target_bg_color)
        steps = 7

        def step(idx=1):
            ratio = idx / steps
            current_border = tuple(int(start_border[i] + (end_border[i] - start_border[i]) * ratio) for i in range(3))
            current_bg = tuple(int(start_bg[i] + (end_bg[i] - start_bg[i]) * ratio) for i in range(3))
            self.upload_border_color = self._rgb_to_hex(current_border)
            self.upload_bg_color = self._rgb_to_hex(current_bg)
            self._draw_upload_placeholder()
            if idx < steps:
                self.upload_hover_job = self.after(20, lambda: step(idx + 1))
            else:
                self.upload_hover_job = None

        step()

    def _clear_comment_placeholder(self, event):
        if self.comment_text.get("1.0", "end").strip() == "Type here...":
            self.comment_text.delete("1.0", END)

    def _update_rating_stars(self, selected_rating):
        try:
            value = max(1, min(5, int(str(selected_rating))))
        except ValueError:
            value = 1
        stars = "★" * value + "☆" * (5 - value)
        self.rating_stars.configure(text=stars)

    def _find_movie_index(self, movie):
        for idx, item in enumerate(self.data.get("movies", [])):
            if item is movie or item == movie:
                return idx
        return None

    def edit_current_movie(self):
        """Load current details movie into Add Movie form for editing."""
        movie = self.current_detail_movie
        if not movie:
            self.status_label.configure(text="No movie selected to edit.", text_color="#ff6b6b")
            return
        movie_index = self._find_movie_index(movie)
        if movie_index is None:
            self.status_label.configure(text="Selected movie not found.", text_color="#ff6b6b")
            return

        self.clear_fields()
        self.edit_movie_index = movie_index
        self.name_entry.insert(0, str(movie.get("title", "")))
        self.genre_entry.insert(0, str(movie.get("genre", "")))
        self.actors_entry.insert(0, self._normalize_actors(movie.get("actors", "")))
        self.year_entry.insert(0, str(movie.get("year", "")))

        comment = str(movie.get("comment", "")).strip()
        if comment:
            self.comment_text.delete("1.0", END)
            self.comment_text.insert("1.0", comment)

        rating = str(movie.get("rating", "1"))
        if hasattr(self, "rating_var"):
            self.rating_var.set(rating if rating in {"1", "2", "3", "4", "5"} else "1")
            self._update_rating_stars(self.rating_var.get())

        image_path = self._resolve_image_path(movie)
        self.selected_image_path = image_path
        if image_path:
            self.image_label.configure(text=os.path.basename(image_path), text_color="white")

        if hasattr(self, "save_movie_btn"):
            self.save_movie_btn.configure(text="Update")
        self.status_label.configure(text="Editing selected movie...", text_color="#b8e84b")
        self.tab_view.set("Add Movie")

    def delete_current_movie(self):
        """Delete current movie from collection."""
        movie = self.current_detail_movie
        if not movie:
            return
        movie_index = self._find_movie_index(movie)
        if movie_index is None:
            return

        title = str(self.data["movies"][movie_index].get("title", "Movie"))
        del self.data["movies"][movie_index]
        self.save_data()
        self.current_detail_movie = None
        self.refresh_movie_details()
        self.refresh_movie_list()
        self.refresh_movies_page()
        self.status_label.configure(text=f"✓ '{title}' deleted successfully!", text_color="#b8e84b")
        self.tab_view.set("Movies Page")

if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()