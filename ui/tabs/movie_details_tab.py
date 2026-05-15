from customtkinter import CTkFrame, CTkLabel, CTkTextbox, CTkButton



def setup_movie_details_tab(app):
    """Build Movie Details tab UI and attach widgets to app."""

    tab = app.tab_view.tab("Movie Details")
    tab.configure(fg_color="#1f1f1f")

    app.current_detail_movie = None

    page = CTkFrame(tab, fg_color="#1f1f1f")
    page.pack(fill="both", expand=True, padx=14, pady=14)

    shell = CTkFrame(page, fg_color="transparent")
    shell.pack(fill="both", expand=True)

    app._build_sidebar(shell, "menu")

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

    app.details_body = body
    app.details_body.bind("<Configure>", app._on_details_body_configure)

    left_col = CTkFrame(body, fg_color="transparent")
    left_col.grid(row=0, column=0, sticky="nsew")
    left_col.grid_propagate(False)

    app.details_left_col = left_col
    app.details_left_col.bind("<Configure>", app._on_details_left_col_configure)

    right_col = CTkFrame(body, fg_color="transparent")
    right_col.grid(row=0, column=2, sticky="nsew")
    right_col.grid_propagate(False)

    # Poster
    app.details_poster_box = CTkFrame(left_col, fg_color="#2f2f2f", corner_radius=12, height=330)
    app.details_poster_box.pack(fill="x", pady=(0, 10))
    app.details_poster_box.pack_propagate(False)

    app.details_poster_label = CTkLabel(app.details_poster_box, text="")
    app.details_poster_label.pack(fill="both", expand=True, padx=6, pady=6)

    app.details_poster_box.bind("<Configure>", lambda _e: app.refresh_movie_details())

    # Title
    app.details_title_label = CTkLabel(
        left_col,
        text="No movie selected",
        anchor="w",
        font=("Arial", 18, "bold")
    )
    app.details_title_label.pack(fill="x", pady=(0, 2))

    CTkLabel(
        left_col,
        text="My comment",
        anchor="w",
        text_color="#b8e84b",
        font=("Arial", 16, "bold")
    ).pack(fill="x", pady=(0, 4))

    app.details_comment_box = CTkTextbox(
        left_col,
        fg_color="#1f1f1f",
        border_width=0,
        text_color="#d8d8d8",
        font=("Arial", 13),
        wrap="word"
    )
    app.details_comment_box.pack(fill="both", expand=True)
    app.details_comment_box.insert("1.0", "Open a movie details card to preview full information.")
    app.details_comment_box.configure(state="disabled")

    # Right column info
    CTkLabel(right_col, text="My Rating", anchor="w",
             text_color="#b8e84b", font=("Arial", 16, "bold")).pack(fill="x", pady=(10, 2))

    app.details_rating_label = CTkLabel(
        right_col,
        text="☆☆☆☆☆",
        anchor="w",
        text_color="#b8e84b",
        font=("Arial", 30, "bold")
    )
    app.details_rating_label.pack(fill="x", pady=(0, 10))

    app.details_year_label = CTkLabel(right_col, text="Year: -", anchor="w",
                                     font=("Arial", 14, "bold"))
    app.details_year_label.pack(fill="x", pady=(0, 8))

    app.details_actors_label = CTkLabel(right_col, text="Actors: -", anchor="w",
                                       font=("Arial", 14, "bold"))
    app.details_actors_label.pack(fill="x", pady=(0, 8))

    app.details_genre_label = CTkLabel(right_col, text="Genre: -", anchor="w",
                                      font=("Arial", 14, "bold"))
    app.details_genre_label.pack(fill="x", pady=(0, 14))

    CTkLabel(right_col, text="Currently watching", anchor="w",
             font=("Arial", 16, "bold")).pack(fill="x", pady=(8, 8))

    app.details_watch_frame = CTkFrame(right_col, fg_color="#2f2f2f", corner_radius=10)
    app.details_watch_frame.pack(fill="x")

    # Actions
    details_actions = CTkFrame(right_col, fg_color="transparent")
    details_actions.pack(fill="x", pady=(12, 0))

    CTkButton(
        details_actions,
        text="Edit",
        height=app.std_btn_height,
        fg_color="#b8e84b",
        text_color="black",
        hover_color="#c8f15f",
        font=app.std_btn_font,
        command=app.edit_current_movie
    ).pack(side="left", fill="x", expand=True, padx=(0, 8))

    CTkButton(
        details_actions,
        text="Delete",
        height=app.std_btn_height,
        fg_color="#c14f4f",
        text_color="white",
        hover_color="#d25f5f",
        font=app.std_btn_font,
        command=app.delete_current_movie
    ).pack(side="left", fill="x", expand=True)

    app.refresh_movie_details()