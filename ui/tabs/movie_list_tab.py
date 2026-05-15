from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton



def setup_movie_list_tab(app):
    """Home page (Movie List tab) UI."""

    tab = app.tab_view.tab("Movie List")
    tab.configure(fg_color="#1f1f1f")

    app._ui_images = []
    app.friend_rows = []

    page = CTkFrame(tab, fg_color="#1f1f1f")
    page.pack(fill="both", expand=True, padx=14, pady=14)

    app._build_sidebar(page, "home")

    content = CTkFrame(page, fg_color="transparent")
    content.pack(side="left", fill="both", expand=True)

    app.home_content = content

    content.grid_columnconfigure(0, weight=65)
    content.grid_columnconfigure(1, weight=0, minsize=12)
    content.grid_columnconfigure(2, weight=35)
    content.grid_rowconfigure(0, weight=1)

    content.bind("<Configure>", app._on_home_content_configure)

    left_column = CTkFrame(content, fg_color="transparent")
    left_column.grid(row=0, column=0, sticky="nsew")

    app.home_left_column = left_column
    app.home_left_column.bind("<Configure>", app._on_home_left_column_configure)

    right_column = CTkFrame(content, fg_color="transparent")
    right_column.grid(row=0, column=2, sticky="nsew")

    app.home_right_column = right_column

    # ---------------- TOP BAR ----------------
    top_bar = CTkFrame(left_column, fg_color="transparent")
    top_bar.pack(fill="x", pady=(0, 10))

    search_wrap = CTkFrame(
        top_bar,
        fg_color="#2f2f2f",
        corner_radius=8,
        width=430,
        height=app.std_btn_height + 6
    )
    search_wrap.pack(side="left", padx=(0, 10))
    search_wrap.pack_propagate(False)

    app.search_bar = CTkEntry(
        search_wrap,
        width=360,
        height=34,
        placeholder_text="Search",
        fg_color="#2f2f2f",
        border_width=0
    )
    app.search_bar.pack(side="left", fill="y", padx=(10, 46))
    app.search_bar.bind("<KeyRelease>", app.apply_filter)

    app.search_btn = CTkButton(
        search_wrap,
        text="",
        image=app.search_icon_image,
        width=28,
        height=28,
        corner_radius=6,
        fg_color="#c5ef4d",
        text_color="black",
        hover_color="#d3f767",
        font=app.std_btn_font,
        command=app.apply_filter
    )
    app.search_btn.place(relx=1.0, rely=0.5, x=-8, anchor="e")

    # ---------------- FILTER ----------------
    app.home_filter_field = "Name"
    app.filter_buttons = {}

    filter_wrap = CTkFrame(top_bar, fg_color="transparent")
    filter_wrap.pack(side="left")

    for option in ["Name", "Genre", "Actors", "Years"]:
        btn = CTkButton(
            filter_wrap,
            text=option,
            width=86,
            height=app.std_btn_height,
            corner_radius=8,
            fg_color="#2f2f2f",
            text_color="white",
            hover_color="#3f3f3f",
            font=app.std_btn_font,
            command=lambda value=option: app._set_home_filter(value)
        )
        btn.pack(side="left", padx=(0, 6))
        app.filter_buttons[option] = btn

    app._set_home_filter("Name", refresh=False)

    # ---------------- HERO ----------------
    app.hero_frame = CTkFrame(left_column, fg_color="transparent", height=340)
    app.hero_frame.pack(fill="x", pady=(0, 16))
    app.hero_frame.pack_propagate(False)

    app.hero_image_label = CTkLabel(app.hero_frame, text="")
    app.hero_image_label.pack(fill="both", expand=True)

    app.hero_frame.bind("<Configure>", app._on_hero_frame_configure)

    # ---------------- GRID ----------------
    CTkLabel(left_column, text="Popular movies", font=("Arial", 16, "bold")).pack(fill="x", pady=(0, 8))

    app.cards_grid = CTkFrame(left_column, fg_color="transparent")
    app.cards_grid.pack(fill="x")

    # ---------------- RIGHT PANEL ----------------
    profile_box = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10, height=40)
    profile_box.pack(fill="x", pady=(0, 10))
    profile_box.pack_propagate(False)

    CTkLabel(profile_box, text="Movie dashboard", font=("Arial", 14, "bold")).pack(side="left", padx=12)

    CTkButton(
        right_column,
        text="+ Add new",
        height=app.std_btn_height,
        font=app.std_btn_font,
        fg_color="#c5ef4d",
        text_color="black",
        hover_color="#d3f767",
        command=lambda: app.tab_view.set("Add Movie")
    ).pack(fill="x", pady=(0, 12))

    CTkLabel(right_column, text="Currently watching", font=("Arial", 16, "bold")).pack(fill="x", pady=(4, 8))

    app.recent_frame = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10)
    app.recent_frame.pack(fill="both", expand=True, pady=(0, 16))

    CTkLabel(right_column, text="Movie Journal", font=("Arial", 16, "bold")).pack(fill="x", pady=(2, 8))

    app.journal_frame = CTkFrame(right_column, fg_color="#2f2f2f", corner_radius=10)
    app.journal_frame.pack(fill="both", expand=True)

    app.journal_frame.bind("<Configure>", lambda _e: app._resize_home_journal())

    app._render_movie_journal()

    app.refresh_movie_list()
    app.after(120, app.refresh_movie_list)
    app.after(320, app.refresh_movie_list)