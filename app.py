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
        os.makedirs(self.images_dir, exist_ok=True)

        # Image state for current movie
        self.selected_image_path = None

        self.load_data()
        
        # App color base
        self.configure(fg_color="#191919")
        self.std_btn_height = 34
        self.std_btn_font = ("Arial", 12, "bold")
        self._ctk_image_cache = {}
        self._movies_page_last_signature = None
        self._movies_page_last_width = 0

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
    
    def load_data(self):
        """Load movie data from JSON file"""
        self.data = {"movies": []}
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.data = json.load(file)
    
    def save_data(self):
        """Save movie data to JSON file"""
        with open(self.data_file, "w") as file:
            json.dump(self.data, file, indent=4)

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
            CTkButton(
                buttons_holder,
                text=icon,
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
        CTkButton(
            buttons_row,
            text="Save",
            command=self.add_movie,
            height=self.std_btn_height,
            fg_color="#b8e84b",
            text_color="black",
            hover_color="#c8f15f",
            font=self.std_btn_font
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
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

        left_column = CTkFrame(content, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self.home_left_column = left_column
        self.home_left_column.bind("<Configure>", self._on_home_left_column_configure)

        right_column = CTkFrame(content, width=330, fg_color="transparent")
        right_column.pack(side="left", fill="y")
        right_column.pack_propagate(False)

        # Top bar
        top_bar = CTkFrame(left_column, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        search_wrap = CTkFrame(top_bar, fg_color="#2f2f2f", corner_radius=8)
        search_wrap.pack(side="left", padx=(0, 10))
        self.search_bar = CTkEntry(search_wrap, width=260, height=34, placeholder_text="Search", fg_color="#2f2f2f", border_width=0)
        self.search_bar.pack(side="left", padx=(10, 4))
        self.search_bar.bind("<KeyRelease>", self.apply_filter)
        CTkButton(
            search_wrap,
            text="Q",
            width=32,
            height=self.std_btn_height,
            fg_color="#c5ef4d",
            text_color="black",
            hover_color="#d3f767",
            font=self.std_btn_font,
            command=self.apply_filter
        ).pack(side="left", padx=(0, 8))

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
        self.hero_frame = CTkFrame(left_column, fg_color="#2f2f2f", corner_radius=12, height=340)
        self.hero_frame.pack(fill="x", pady=(0, 16))
        self.hero_frame.pack_propagate(False)
        self.hero_image_label = CTkLabel(self.hero_frame, text="")
        self.hero_image_label.pack(fill="both", expand=True, padx=2, pady=2)
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
        self.recent_frame.pack(fill="x", pady=(0, 14))

        CTkLabel(right_column, text="My Friends", font=("Arial", 16, "bold"), anchor="w").pack(fill="x", pady=(2, 8))
        self.friends_frame = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10)
        self.friends_frame.pack(fill="x")

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

        content = CTkFrame(content_outer, fg_color="transparent", width=1030)
        content.pack(expand=True, fill="both")
        content.pack_propagate(False)

        CTkLabel(content, text="Details", font=("Arial", 22, "bold")).pack(anchor="n", pady=(2, 10))

        body = CTkFrame(content, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1, uniform="details")
        body.grid_columnconfigure(1, weight=0, uniform="details")
        body.grid_rowconfigure(0, weight=1)

        left_col = CTkFrame(body, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        right_col = CTkFrame(body, fg_color="transparent", width=440)
        right_col.grid(row=0, column=1, sticky="ns")
        right_col.grid_propagate(False)

        self.details_poster_box = CTkFrame(left_col, fg_color="#2f2f2f", corner_radius=12, height=330)
        self.details_poster_box.pack(fill="x", pady=(0, 10))
        self.details_poster_box.pack_propagate(False)
        self.details_poster_label = CTkLabel(self.details_poster_box, text="")
        self.details_poster_label.pack(fill="both", expand=True, padx=2, pady=2)

        self.details_title_label = CTkLabel(left_col, text="No movie selected", anchor="w", font=("Arial", 22, "bold"))
        self.details_title_label.pack(fill="x", pady=(0, 2))
        CTkLabel(left_col, text="My comment", anchor="w", text_color="#b8e84b", font=("Arial", 22, "bold")).pack(fill="x", pady=(0, 4))
        self.details_comment_label = CTkLabel(
            left_col,
            text="Open a movie details card to preview full information.",
            justify="left",
            anchor="nw",
            wraplength=620,
            text_color="#d8d8d8",
            font=("Arial", 14)
        )
        self.details_comment_label.pack(fill="both", expand=True)

        CTkLabel(right_col, text="My Rating", anchor="w", text_color="#b8e84b", font=("Arial", 22, "bold")).pack(fill="x", pady=(10, 2))
        self.details_rating_label = CTkLabel(right_col, text="☆☆☆☆☆", anchor="w", text_color="#b8e84b", font=("Arial", 48, "bold"))
        self.details_rating_label.pack(fill="x", pady=(0, 10))

        self.details_year_label = CTkLabel(right_col, text="Year: -", anchor="w", justify="left", wraplength=410, font=("Arial", 16, "bold"))
        self.details_year_label.pack(fill="x", pady=(0, 8))
        self.details_actors_label = CTkLabel(right_col, text="Actors: -", justify="left", wraplength=410, anchor="w", font=("Arial", 16, "bold"))
        self.details_actors_label.pack(fill="x", pady=(0, 8))
        self.details_genre_label = CTkLabel(right_col, text="Genre: -", justify="left", wraplength=410, anchor="w", font=("Arial", 16, "bold"))
        self.details_genre_label.pack(fill="x", pady=(0, 14))

        CTkLabel(right_col, text="Currently watching", anchor="w", font=("Arial", 22, "bold")).pack(fill="x", pady=(8, 8))
        self.details_watch_frame = CTkFrame(right_col, fg_color="#2f2f2f", corner_radius=10)
        self.details_watch_frame.pack(fill="x")

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
            self.details_comment_label.configure(text="Open a movie details card to preview full information.")
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
            poster_img = self._make_image_cover(poster_path, (640, 314))
            if poster_img:
                self.details_poster_label.configure(image=poster_img, text="")
            else:
                self.details_poster_label.configure(image=None, text="No image")

            self.details_title_label.configure(text=title)
            self.details_comment_label.configure(text=comment)
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
            row = CTkFrame(self.details_watch_frame, fg_color="#3a3a3a", corner_radius=8)
            row.pack(fill="x", padx=8, pady=6)
            row_inner = CTkFrame(row, fg_color="transparent")
            row_inner.pack(fill="x", padx=6, pady=6)

            thumb_path = self._resolve_image_path(watch_movie)
            thumb_img = self._make_image_cover(thumb_path, (120, 68))
            if thumb_img:
                CTkLabel(row_inner, image=thumb_img, text="").pack(side="left", padx=(0, 8))
            else:
                CTkLabel(row_inner, text="No image", width=120, height=68, fg_color="#4a4a4a", corner_radius=6).pack(side="left", padx=(0, 8))

            title = str(watch_movie.get("title", "Untitled"))
            year = str(watch_movie.get("year", ""))
            meta = CTkFrame(row_inner, fg_color="transparent")
            meta.pack(side="left", fill="both", expand=True)
            CTkLabel(meta, text=f"{title}  •  {year}", anchor="w", font=("Arial", 18, "bold")).pack(fill="x", pady=(1, 0))
            CTkLabel(meta, text=str(watch_movie.get("genre", "")), anchor="w", text_color="#c9c9c9", font=("Arial", 11)).pack(fill="x")
            CTkButton(
                meta,
                text="Open",
                width=70,
                height=self.std_btn_height,
                fg_color="#b8e84b",
                text_color="black",
                hover_color="#c8f15f",
                font=self.std_btn_font,
                command=lambda m=watch_movie: self.open_movie_details(m)
            ).pack(anchor="e", pady=(4, 0))

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

            mask = Image.new("L", (target_w, target_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, target_w, target_h), radius=radius, fill=255)
            img.putalpha(mask)

            ctk_img = CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
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
        target_h = max(320, min(460, int(column_h * 0.46)))
        if self.hero_frame.cget("height") != target_h:
            self.hero_frame.configure(height=target_h)

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

        hero_img = self._make_image_cover(hero_path, (hero_w, hero_h))
        if hero_img:
            self.hero_image_label.configure(image=hero_img, text="")
        else:
            self.hero_image_label.configure(image=None, text="No image")

    def refresh_movie_list(self):
        """Refresh all dashboard areas"""
        filtered_movies = self._get_filtered_movies()
        self._ui_images = []
        poster_movies = self._movies_with_posters(filtered_movies)
        all_poster_movies = self._movies_with_posters(self.data.get("movies", []))

        # Hero image
        self.current_hero_movie = poster_movies[0] if poster_movies else (all_poster_movies[0] if all_poster_movies else None)
        self.after_idle(self._render_hero_image)

        # Cards
        for widget in self.cards_grid.winfo_children():
            widget.destroy()

        card_pool = poster_movies if poster_movies else all_poster_movies
        card_movies = []
        if card_pool:
            idx = 0
            while len(card_movies) < 3:
                card_movies.append(card_pool[idx % len(card_pool)])
                idx += 1
        if not card_movies:
            CTkLabel(self.cards_grid, text="No movies found for this filter.", text_color="lightgray").pack(anchor="w")
        else:
            for movie in card_movies:
                card = CTkFrame(self.cards_grid, fg_color="#2b2b2b", corner_radius=12, width=248, height=228, border_width=1, border_color="#3d3d3d")
                card.pack(side="left", fill="y", padx=(0, 12), pady=(0, 10))
                card.pack_propagate(False)

                poster_path = self._resolve_image_path(movie)
                poster_img = self._make_image_cover_rounded(poster_path, (232, 122), radius=10)
                if poster_img:
                    CTkLabel(card, image=poster_img, text="").pack(pady=(8, 6), padx=8)
                else:
                    CTkLabel(card, text="No image", width=232, height=122, fg_color="#444444", corner_radius=8).pack(pady=(8, 6), padx=8)

                CTkLabel(card, text=str(movie.get("title", "Unknown")), font=("Arial", 16, "bold"), anchor="w").pack(fill="x", padx=10)
                info_row = CTkFrame(card, fg_color="transparent")
                info_row.pack(fill="x", padx=10, pady=(0, 6))
                CTkLabel(info_row, text=str(movie.get("genre", "")), text_color="#bdbdbd", anchor="w", font=("Arial", 12)).pack(side="left")
                rating = self._movie_rating_value(movie)
                CTkLabel(info_row, text=f"{rating} ★" if rating else "☆", text_color="#b8e84b", anchor="e", font=("Arial", 12, "bold")).pack(side="right")
                CTkButton(
                    card,
                    text="Details",
                    height=self.std_btn_height,
                    fg_color="#b8e84b",
                    text_color="black",
                    hover_color="#c8f15f",
                    font=self.std_btn_font,
                    command=lambda m=movie: self.open_movie_details(m)
                ).pack(fill="x", padx=10, pady=(2, 10))

        # Recently added
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
        watching_source = all_poster_movies if all_poster_movies else self.data.get("movies", [])
        watching_movies = watching_source[-3:][::-1]
        if watching_movies:
            while len(watching_movies) < 3:
                watching_movies.append(watching_movies[-1])

        for movie in watching_movies:
            title = str(movie.get("title", "Untitled"))
            year = str(movie.get("year", ""))
            row = CTkFrame(self.recent_frame, fg_color="#3a3a3a", corner_radius=8)
            row.pack(fill="x", padx=8, pady=6)
            row_inner = CTkFrame(row, fg_color="transparent")
            row_inner.pack(fill="x", padx=6, pady=6)
            thumb_path = self._resolve_image_path(movie)
            thumb_img = self._make_image(thumb_path, (86, 48))
            if thumb_img:
                CTkLabel(row_inner, image=thumb_img, text="").pack(side="left", padx=(0, 8))
            meta = CTkFrame(row_inner, fg_color="transparent")
            meta.pack(side="left", fill="both", expand=True)
            CTkLabel(meta, text=f"{title} • {year}", anchor="w", font=("Arial", 14, "bold")).pack(fill="x", pady=(2, 1))
            CTkLabel(meta, text=str(movie.get("genre", "")), anchor="w", text_color="lightgray").pack(fill="x")

        for widget in self.friends_frame.winfo_children():
            widget.destroy()

        for _ in range(3):
            friend_row = CTkFrame(self.friends_frame, fg_color="#3a3a3a", corner_radius=8)
            friend_row.pack(fill="x", padx=8, pady=6)
            CTkLabel(friend_row, text="●", text_color="#61a5ff", font=("Arial", 18, "bold")).pack(side="left", padx=(10, 8))
            CTkLabel(friend_row, text="Movie buddy", font=("Arial", 14, "bold")).pack(side="left")
            CTkButton(
                friend_row,
                text="See movie list",
                width=120,
                height=self.std_btn_height,
                fg_color="#c5ef4d",
                text_color="black",
                hover_color="#d3f767",
                font=self.std_btn_font
            ).pack(side="right", padx=10, pady=8)
    
    
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

        movie = {
            "title": name,
            "genre": genre,
            "actors": actors,
            "year": year,
            "image": image_path_value,
            "comment": comment_text,
            "rating": self.rating_var.get() if hasattr(self, "rating_var") else "1"
        }
        
        # Add to data and save
        self.data["movies"].append(movie)
        self.save_data()
        
        # Show success message
        self.status_label.configure(text=f"✓ '{name}' added successfully!", text_color="green")
        
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

if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()