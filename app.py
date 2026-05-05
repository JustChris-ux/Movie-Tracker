import json
from customtkinter import *
from tkinter import filedialog
import os
import shutil
from PIL import Image

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
    
    def setup_add_movie_tab(self):
        """Setup the Add Movie tab in the provided 1:1 style."""
        tab = self.tab_view.tab("Add Movie")
        tab.configure(fg_color="#1f1f1f")

        page = CTkFrame(tab, fg_color="#1f1f1f")
        page.pack(fill="both", expand=True, padx=10, pady=10)

        left_menu = CTkFrame(page, width=58, fg_color="#2c2c2c", corner_radius=12)
        left_menu.pack(side="left", fill="y", padx=(0, 12))
        left_menu.pack_propagate(False)

        CTkButton(left_menu, text="⌂", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Movie List")).pack(pady=(24, 10))
        CTkButton(left_menu, text="+", width=34, height=34, fg_color="#b8e84b", text_color="black", hover_color="#c8f15f").pack(pady=8)
        CTkButton(left_menu, text="☰", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Movies Page")).pack(pady=8)

        content = CTkFrame(page, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)

        header = CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(4, 14))
        CTkLabel(header, text="Add new movie", font=("Arial", 30, "bold")).pack(anchor="n")
        CTkLabel(header, text="Track your personal movie collection", font=("Arial", 13), text_color="#b8b8b8").pack(anchor="n", pady=(2, 0))

        body = CTkFrame(content, fg_color="transparent")
        body.pack(fill="both", expand=True)

        left_card = CTkFrame(body, fg_color="#2b2b2b", corner_radius=12)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right_card = CTkFrame(body, fg_color="#2b2b2b", corner_radius=12, width=430)
        right_card.pack(side="left", fill="y")
        right_card.pack_propagate(False)

        CTkLabel(left_card, text="About movie", font=("Arial", 30, "bold"), anchor="w").pack(fill="x", padx=24, pady=(18, 12))

        upload_box = CTkFrame(left_card, fg_color="#545454", corner_radius=10)
        upload_box.pack(fill="x", padx=24, pady=(0, 14))
        self.upload_btn = CTkButton(
            upload_box,
            text="+\nUpload poster",
            command=self.choose_image,
            width=420,
            height=120,
            fg_color="#545454",
            hover_color="#636363",
            text_color="#b8e84b",
            border_width=2,
            border_color="#b8e84b",
            font=("Arial", 18, "bold")
        )
        self.upload_btn.pack(fill="x", padx=6, pady=6)

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
            height=44,
            fg_color="#b8e84b",
            text_color="black",
            hover_color="#c8f15f",
            font=("Arial", 20, "bold")
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        CTkButton(
            buttons_row,
            text="Clear fields",
            command=self.clear_fields,
            height=44,
            fg_color="#f0f0f0",
            text_color="black",
            hover_color="#ffffff",
            font=("Arial", 20, "bold")
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
        page.pack(fill="both", expand=True, padx=12, pady=12)

        left_menu = CTkFrame(page, width=58, fg_color="#2c2c2c", corner_radius=12)
        left_menu.pack(side="left", fill="y", padx=(0, 12))
        left_menu.pack_propagate(False)

        CTkButton(left_menu, text="H", width=34, height=34, fg_color="#c5ef4d", text_color="black", hover_color="#d3f767").pack(pady=(24, 10))
        CTkButton(left_menu, text="+", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Add Movie")).pack(pady=8)
        CTkButton(left_menu, text="M", width=34, height=34, fg_color="#d0d0d0", text_color="black", hover_color="#e8e8e8", command=lambda: self.tab_view.set("Movies Page")).pack(pady=8)

        content = CTkFrame(page, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)

        left_column = CTkFrame(content, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 12))

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
        CTkButton(search_wrap, text="Q", width=28, height=26, fg_color="#c5ef4d", text_color="black", hover_color="#d3f767", command=self.apply_filter).pack(side="left", padx=(0, 8))

        self.filter_segment = CTkSegmentedButton(
            top_bar,
            values=["Name", "Genre", "Actors", "Years"],
            width=360,
            height=34,
            fg_color="#2f2f2f",
            selected_color="#c5ef4d",
            selected_hover_color="#d3f767",
            unselected_color="#2f2f2f",
            unselected_hover_color="#404040",
            text_color="white",
            command=lambda _: self.apply_filter()
        )
        self.filter_segment.pack(side="left")
        self.filter_segment.set("Name")

        # Hero and cards
        self.hero_frame = CTkFrame(left_column, fg_color="#2f2f2f", corner_radius=12, height=300)
        self.hero_frame.pack(fill="x", pady=(0, 16))
        self.hero_frame.pack_propagate(False)
        self.hero_image_label = CTkLabel(self.hero_frame, text="")
        self.hero_image_label.pack(fill="both", expand=True, padx=2, pady=2)

        CTkLabel(left_column, text="Popular movies", font=("Arial", 34, "bold"), anchor="w").pack(fill="x", pady=(0, 8))
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
            height=44,
            font=("Arial", 32, "bold"),
            fg_color="#c5ef4d",
            text_color="black",
            hover_color="#d3f767",
            command=lambda: self.tab_view.set("Add Movie")
        ).pack(fill="x", pady=(0, 12))

        CTkLabel(right_column, text="Currently watching", font=("Arial", 28, "bold"), anchor="w").pack(fill="x", pady=(4, 8))
        self.recent_frame = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10)
        self.recent_frame.pack(fill="x", pady=(0, 14))

        CTkLabel(right_column, text="My Friends", font=("Arial", 28, "bold"), anchor="w").pack(fill="x", pady=(2, 8))
        self.friends_frame = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10)
        self.friends_frame.pack(fill="x")

        self.refresh_movie_list()
        self.after(120, self.refresh_movie_list)

    def apply_filter(self, event=None):
        """Apply filter and re-render dashboard widgets"""
        self.refresh_movie_list()

    def setup_movies_page_tab(self):
        """Setup dedicated page for all movies in grid view."""
        tab = self.tab_view.tab("Movies Page")
        tab.configure(fg_color="#1f1f1f")

        self.movies_page_images = []

        page = CTkFrame(tab, fg_color="#1f1f1f")
        page.pack(fill="both", expand=True, padx=12, pady=12)

        left_menu = CTkFrame(page, width=58, fg_color="#2c2c2c", corner_radius=12)
        left_menu.pack(side="left", fill="y", padx=(0, 12))
        left_menu.pack_propagate(False)
        CTkButton(left_menu, text="⌂", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Movie List")).pack(pady=(24, 10))
        CTkButton(left_menu, text="+", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Add Movie")).pack(pady=8)
        CTkButton(left_menu, text="☰", width=34, height=34, fg_color="#b8e84b", text_color="black", hover_color="#c8f15f").pack(pady=8)

        content = CTkFrame(page, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)

        CTkLabel(content, text="My movie list", font=("Arial", 34, "bold")).pack(anchor="n", pady=(6, 12))

        self.movies_sort_segment = CTkSegmentedButton(
            content,
            values=["Recently watched", "Highest rated", "Most popular"],
            width=520,
            height=46,
            fg_color="#3f3f3f",
            selected_color="#b8e84b",
            selected_hover_color="#c8f15f",
            unselected_color="#4a4a4a",
            unselected_hover_color="#5a5a5a",
            text_color="white",
            command=lambda _: self.refresh_movies_page()
        )
        self.movies_sort_segment.pack(anchor="w", pady=(0, 14))
        self.movies_sort_segment.set("Recently watched")

        self.movies_scroll = CTkScrollableFrame(content, fg_color="#1f1f1f", corner_radius=0)
        self.movies_scroll.pack(fill="both", expand=True)

        self.refresh_movies_page()

    def _movie_rating_value(self, movie):
        try:
            return int(str(movie.get("rating", "0")))
        except ValueError:
            return 0

    def _sorted_movies_for_page(self):
        movies = list(self.data.get("movies", []))
        mode = self.movies_sort_segment.get() if hasattr(self, "movies_sort_segment") else "Recently watched"
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

        self.movies_page_images = []
        for widget in self.movies_scroll.winfo_children():
            widget.destroy()

        movies = self._sorted_movies_for_page()
        if not movies:
            CTkLabel(self.movies_scroll, text="No movies yet. Add your first one from Add Movie.", text_color="lightgray").pack(anchor="w", padx=10, pady=10)
            return

        columns = 4
        row_frame = None
        for idx, movie in enumerate(movies):
            if idx % columns == 0:
                row_frame = CTkFrame(self.movies_scroll, fg_color="transparent")
                row_frame.pack(fill="x", pady=(0, 14))

            card = CTkFrame(row_frame, fg_color="#2f2f2f", corner_radius=10, width=235, height=210)
            card.pack(side="left", padx=(0, 14))
            card.pack_propagate(False)

            poster_path = self._resolve_image_path(movie)
            poster_img = self._make_image_cover(poster_path, (220, 110))
            if poster_img:
                self.movies_page_images.append(poster_img)
                CTkLabel(card, image=poster_img, text="").pack(padx=8, pady=(8, 6))
            else:
                CTkLabel(card, text="No image", width=220, height=110, fg_color="#444444", corner_radius=8).pack(padx=8, pady=(8, 6))

            title = str(movie.get("title", "Unknown"))
            genre = str(movie.get("genre", ""))
            rating = self._movie_rating_value(movie)
            stars = "★" * max(0, min(5, rating))
            CTkLabel(card, text=title, anchor="w", font=("Arial", 16, "bold")).pack(fill="x", padx=8)
            CTkLabel(card, text=genre, anchor="w", text_color="#a8a8a8", font=("Arial", 12)).pack(fill="x", padx=8, pady=(0, 4))
            CTkLabel(card, text=f"{stars}", anchor="e", text_color="#b8e84b").pack(fill="x", padx=8, pady=(0, 4))
            CTkButton(
                card,
                text="Details",
                height=28,
                fg_color="#b8e84b",
                text_color="black",
                hover_color="#c8f15f",
                command=lambda m=movie: self.open_movie_details(m)
            ).pack(fill="x", padx=8, pady=(0, 8))

    def setup_movie_details_tab(self):
        """Setup single movie details page."""
        tab = self.tab_view.tab("Movie Details")
        tab.configure(fg_color="#1f1f1f")

        self.current_detail_movie = None

        page = CTkFrame(tab, fg_color="#1f1f1f")
        page.pack(fill="both", expand=True, padx=12, pady=12)

        left_menu = CTkFrame(page, width=58, fg_color="#2c2c2c", corner_radius=12)
        left_menu.pack(side="left", fill="y", padx=(0, 12))
        left_menu.pack_propagate(False)
        CTkButton(left_menu, text="⌂", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Movie List")).pack(pady=(24, 10))
        CTkButton(left_menu, text="+", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Add Movie")).pack(pady=8)
        CTkButton(left_menu, text="☰", width=34, height=34, fg_color="#f0f0f0", text_color="black", hover_color="#ffffff", command=lambda: self.tab_view.set("Movies Page")).pack(pady=8)

        content = CTkFrame(page, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)

        CTkLabel(content, text="Details", font=("Arial", 36, "bold")).pack(anchor="n", pady=(6, 10))

        body = CTkFrame(content, fg_color="transparent")
        body.pack(fill="both", expand=True)

        left_col = CTkFrame(body, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 16))

        right_col = CTkFrame(body, fg_color="transparent", width=420)
        right_col.pack(side="left", fill="y")
        right_col.pack_propagate(False)

        self.details_poster_box = CTkFrame(left_col, fg_color="#2f2f2f", corner_radius=10, height=360)
        self.details_poster_box.pack(fill="x", pady=(0, 10))
        self.details_poster_box.pack_propagate(False)
        self.details_poster_label = CTkLabel(self.details_poster_box, text="")
        self.details_poster_label.pack(fill="both", expand=True, padx=2, pady=2)

        self.details_title_label = CTkLabel(left_col, text="No movie selected", anchor="w", font=("Arial", 42, "bold"))
        self.details_title_label.pack(fill="x", pady=(0, 2))
        CTkLabel(left_col, text="My comment", anchor="w", text_color="#b8e84b", font=("Arial", 34, "bold")).pack(fill="x", pady=(0, 4))
        self.details_comment_label = CTkLabel(
            left_col,
            text="Open a movie details card to preview full information.",
            justify="left",
            anchor="nw",
            wraplength=620,
            text_color="#d8d8d8",
            font=("Arial", 26)
        )
        self.details_comment_label.pack(fill="both", expand=True)

        CTkLabel(right_col, text="My Rating", anchor="w", text_color="#b8e84b", font=("Arial", 36, "bold")).pack(fill="x", pady=(10, 4))
        self.details_rating_label = CTkLabel(right_col, text="☆☆☆☆☆", anchor="w", text_color="#b8e84b", font=("Arial", 48))
        self.details_rating_label.pack(fill="x", pady=(0, 10))

        self.details_year_label = CTkLabel(right_col, text="Year: -", anchor="w", font=("Arial", 34, "bold"))
        self.details_year_label.pack(fill="x", pady=(0, 10))
        self.details_actors_label = CTkLabel(right_col, text="Actors: -", justify="left", wraplength=390, anchor="w", font=("Arial", 32, "bold"))
        self.details_actors_label.pack(fill="x", pady=(0, 10))
        self.details_genre_label = CTkLabel(right_col, text="Genre: -", justify="left", wraplength=390, anchor="w", font=("Arial", 32, "bold"))
        self.details_genre_label.pack(fill="x", pady=(0, 14))

        CTkLabel(right_col, text="Currently watching", anchor="w", font=("Arial", 24, "bold")).pack(fill="x", pady=(8, 8))
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
            poster_img = self._make_image_cover(poster_path, (660, 340))
            if poster_img:
                self.details_poster_label.configure(image=poster_img, text="")
            else:
                self.details_poster_label.configure(image=None, text="No image")

            self.details_title_label.configure(text=title)
            self.details_comment_label.configure(text=comment)
            self.details_rating_label.configure(text=stars)
            self.details_year_label.configure(text=f"Year: {year}")
            self.details_actors_label.configure(text=f"Actors: {actors}")
            self.details_genre_label.configure(text=f"Genre: {genre}")

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
            thumb_img = self._make_image_cover(thumb_path, (110, 62))
            if thumb_img:
                CTkLabel(row_inner, image=thumb_img, text="").pack(side="left", padx=(0, 8))
            else:
                CTkLabel(row_inner, text="No image", width=110, height=62, fg_color="#4a4a4a", corner_radius=6).pack(side="left", padx=(0, 8))

            title = str(watch_movie.get("title", "Untitled"))
            year = str(watch_movie.get("year", ""))
            meta = CTkFrame(row_inner, fg_color="transparent")
            meta.pack(side="left", fill="both", expand=True)
            CTkLabel(meta, text=f"{title}  •  {year}", anchor="w", font=("Arial", 18, "bold")).pack(fill="x", pady=(2, 1))
            CTkLabel(meta, text=str(watch_movie.get("genre", "")), anchor="w", text_color="#c9c9c9").pack(fill="x")
            CTkButton(
                meta,
                text="Open",
                width=70,
                height=24,
                fg_color="#b8e84b",
                text_color="black",
                hover_color="#c8f15f",
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
            img = Image.open(image_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            ctk_img = CTkImage(light_image=img, dark_image=img, size=size)
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
            img = Image.open(image_path)
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
            self._ui_images.append(ctk_img)
            return ctk_img
        except Exception:
            return None

    def _get_filtered_movies(self):
        filter_text = self.search_bar.get().strip().lower()
        field = self.filter_segment.get()
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

    def refresh_movie_list(self):
        """Refresh all dashboard areas"""
        filtered_movies = self._get_filtered_movies()
        self._ui_images = []
        poster_movies = self._movies_with_posters(filtered_movies)
        all_poster_movies = self._movies_with_posters(self.data.get("movies", []))

        # Hero image
        hero_movie = poster_movies[0] if poster_movies else (all_poster_movies[0] if all_poster_movies else None)
        hero_path = self._resolve_image_path(hero_movie) if hero_movie else None
        self.update_idletasks()
        hero_w = max(self.hero_frame.winfo_width() - 4, 300)
        hero_h = max(self.hero_frame.winfo_height() - 4, 180)
        hero_img = self._make_image_cover(hero_path, (hero_w, hero_h))
        if hero_img:
            self.hero_image_label.configure(image=hero_img, text="")
        else:
            self.hero_image_label.configure(image=None, text="No image")

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
                card = CTkFrame(self.cards_grid, fg_color="#2f2f2f", corner_radius=10)
                card.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=(0, 10))

                poster_path = self._resolve_image_path(movie)
                poster_img = self._make_image(poster_path, (228, 120))
                if poster_img:
                    CTkLabel(card, image=poster_img, text="").pack(pady=(8, 6))
                else:
                    CTkLabel(card, text="No image", width=228, height=120).pack(pady=(8, 6))

                CTkLabel(card, text=str(movie.get("title", "Unknown")), font=("Arial", 16, "bold"), anchor="w").pack(fill="x", padx=10)
                CTkLabel(card, text=str(movie.get("genre", "")), text_color="lightgray", anchor="w").pack(fill="x", padx=10, pady=(0, 6))
                CTkButton(
                    card,
                    text="Details",
                    height=30,
                    fg_color="#b8e84b",
                    text_color="black",
                    hover_color="#c8f15f",
                    command=lambda m=movie: self.open_movie_details(m)
                ).pack(fill="x", padx=10, pady=(0, 10))

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
                height=28,
                fg_color="#c5ef4d",
                text_color="black",
                hover_color="#d3f767",
                font=("Arial", 12, "bold")
            ).pack(side="right", padx=10, pady=8)
    
    
    def add_movie(self):
        """Add a new movie to the collection"""
        # Get values from entries
        name = self.name_entry.get().strip()
        genre = self.genre_entry.get().strip()
        actors = self.actors_entry.get().strip()
        year = self.year_entry.get().strip()
        
        # Validate inputs
        if not name:
            self.status_label.configure(text="Please enter a movie name!", text_color="red")
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