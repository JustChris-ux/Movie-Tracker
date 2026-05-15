
from tkinter import Canvas, StringVar
from customtkinter import (
    CTkFrame, CTkLabel, CTkEntry, CTkTextbox,
    CTkButton, CTkOptionMenu
)


def setup_add_movie_tab(app):
    """Build Add Movie tab UI and attach widgets to app."""

    tab = app.tab_view.tab("Add Movie")
    tab.configure(fg_color="#1f1f1f")

    page = CTkFrame(tab, fg_color="#1f1f1f")
    page.pack(fill="both", expand=True, padx=14, pady=14)

    app._build_sidebar(page, "add")

    content = CTkFrame(page, fg_color="transparent")
    content.pack(side="left", fill="both", expand=True)

    header = CTkFrame(content, fg_color="transparent")
    header.pack(fill="x", pady=(4, 14))

    CTkLabel(header, text="Add new movie", font=("Arial", 22, "bold")).pack(anchor="n")
    CTkLabel(
        header,
        text="Track your personal movie collection",
        font=("Arial", 13),
        text_color="#b8b8b8"
    ).pack(anchor="n", pady=(2, 0))

    body = CTkFrame(content, fg_color="transparent")
    body.pack(fill="both", expand=True)

    # LEFT CARD
    left_card = CTkFrame(body, fg_color="#2b2b2b", corner_radius=12)
    left_card.pack(side="left", fill="both", expand=True, padx=(0, 14))

    app.add_left_card = left_card
    app.add_left_card.bind("<Configure>", app._on_add_left_card_configure)

    # RIGHT CARD
    right_card = CTkFrame(body, fg_color="#2b2b2b", corner_radius=12, width=430)
    right_card.pack(side="left", fill="y")
    right_card.pack_propagate(False)

    # Title
    CTkLabel(
        left_card,
        text="About movie",
        font=("Arial", 22, "bold"),
        anchor="w"
    ).pack(fill="x", padx=24, pady=(18, 12))

    # Upload box
    upload_box = CTkFrame(left_card, fg_color="#545454", corner_radius=10)
    upload_box.pack(fill="x", padx=24, pady=(0, 14))

    app.upload_box = upload_box

    app.upload_canvas = Canvas(
        upload_box,
        height=126,
        bg="#545454",
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )
    app.upload_canvas.pack(fill="x", padx=6, pady=6)

    app.upload_border_base_color = "#b8e84b"
    app.upload_border_hover_color = "#d7ff6a"
    app.upload_border_color = app.upload_border_base_color

    app.upload_bg_base_color = "#545454"
    app.upload_bg_hover_color = "#626262"
    app.upload_bg_color = app.upload_bg_base_color

    app.upload_hover_job = None

    app.upload_canvas.bind("<Button-1>", lambda _e: app.choose_image())
    app.upload_canvas.bind("<Configure>", app._draw_upload_placeholder)
    app.upload_canvas.bind(
        "<Enter>",
        lambda _e: app._animate_upload_hover(
            app.upload_border_hover_color,
            app.upload_bg_hover_color
        )
    )
    app.upload_canvas.bind(
        "<Leave>",
        lambda _e: app._animate_upload_hover(
            app.upload_border_base_color,
            app.upload_bg_base_color
        )
    )

    # Image label
    app.image_label = CTkLabel(
        left_card,
        text="No image selected",
        font=("Arial", 12),
        text_color="#b8b8b8",
        anchor="w"
    )
    app.image_label.pack(fill="x", padx=24, pady=(0, 8))

    # Entries
    def add_entry(label, placeholder):
        CTkLabel(left_card, text=label, anchor="w").pack(fill="x", padx=24, pady=(2, 4))
        entry = CTkEntry(
            left_card,
            height=40,
            placeholder_text=placeholder,
            fg_color="#5a5a5a",
            border_width=0
        )
        entry.pack(fill="x", padx=24, pady=(0, 10))
        return entry

    app.name_entry = add_entry("Movie title", "Enter title...")
    app.year_entry = add_entry("Year", "Enter year...")
    app.genre_entry = add_entry("Genre", "Genre tag 1, Genre tag 2")
    app.actors_entry = add_entry("Actors", "Enter name of actors...")

    # COMMENT
    CTkLabel(right_card, text="My Comment", anchor="w").pack(fill="x", padx=24, pady=(22, 4))

    app.comment_text = CTkTextbox(right_card, height=240, fg_color="#5a5a5a", border_width=0)
    app.comment_text.pack(fill="x", padx=24, pady=(0, 14))
    app.comment_text.insert("1.0", "Type here...")
    app.comment_text.bind("<FocusIn>", app._clear_comment_placeholder)

    # RATING
    rating_row = CTkFrame(right_card, fg_color="transparent")
    rating_row.pack(fill="x", padx=24, pady=(6, 12))

    CTkLabel(rating_row, text="My Rating", anchor="w").pack(side="left")

    app.rating_var = StringVar(value="1")

    app.rating_menu = CTkOptionMenu(
        rating_row,
        values=["1", "2", "3", "4", "5"],
        variable=app.rating_var,
        width=90,
        fg_color="#5a5a5a",
        button_color="#5a5a5a",
        button_hover_color="#6a6a6a",
        command=app._update_rating_stars
    )
    app.rating_menu.pack(side="left", padx=(12, 10))

    app.rating_stars = CTkLabel(
        rating_row,
        text="★☆☆☆☆",
        font=("Arial", 24),
        text_color="#b8e84b"
    )
    app.rating_stars.pack(side="left", padx=(6, 0))

    # BUTTONS
    buttons_row = CTkFrame(right_card, fg_color="transparent")
    buttons_row.pack(fill="x", padx=24, pady=(16, 8))

    app.save_movie_btn = CTkButton(
        buttons_row,
        text="Save",
        command=app.add_movie,
        height=app.std_btn_height,
        fg_color="#b8e84b",
        text_color="black",
        hover_color="#c8f15f",
        font=app.std_btn_font
    )
    app.save_movie_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

    CTkButton(
        buttons_row,
        text="Clear fields",
        command=app.clear_fields,
        height=app.std_btn_height,
        fg_color="#f0f0f0",
        text_color="black",
        hover_color="#ffffff",
        font=app.std_btn_font
    ).pack(side="left", fill="x", expand=True)

    app.status_label = CTkLabel(right_card, text="", font=("Arial", 13))
    app.status_label.pack(fill="x", padx=24, pady=(6, 0))
