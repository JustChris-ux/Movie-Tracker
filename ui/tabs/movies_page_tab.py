from customtkinter import CTkFrame, CTkLabel, CTkSegmentedButton, CTkScrollableFrame


def setup_movies_page_tab(app):
    """Grid-style Movies Page tab UI."""

    tab = app.tab_view.tab("Movies Page")
    tab.configure(fg_color="#1f1f1f")

    app.movies_page_images = []
    app.movies_sort_mode = "Recently watched"
    app.movies_page_refresh_job = None

    page = CTkFrame(tab, fg_color="#1f1f1f")
    page.pack(fill="both", expand=True, padx=14, pady=14)

    shell = CTkFrame(page, fg_color="transparent")
    shell.pack(fill="both", expand=True)

    app._build_sidebar(shell, "menu")

    content_outer = CTkFrame(shell, fg_color="transparent")
    content_outer.pack(side="left", fill="both", expand=True)

    content = CTkFrame(content_outer, fg_color="transparent", width=1000)
    content.pack(expand=True, fill="both")
    content.pack_propagate(False)

    CTkLabel(
        content,
        text="My movie list",
        font=("Arial", 22, "bold")
    ).pack(anchor="n", pady=(2, 12))

    app.movies_sort_segment = CTkSegmentedButton(
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
        command=app._set_movies_sort_mode
    )
    app.movies_sort_segment.pack(anchor="center", pady=(0, 14))
    app.movies_sort_segment.set(app.movies_sort_mode)
    app._refresh_movies_sort_segment_text()

    app.movies_scroll = CTkScrollableFrame(
        content,
        fg_color="#1f1f1f",
        corner_radius=0,
        scrollbar_button_color="#b8e84b",
        scrollbar_button_hover_color="#c8f15f",
        scrollbar_fg_color="#2a2a2a"
    )
    app.movies_scroll.pack(fill="both", expand=True, pady=(0, 2))

    app.movies_scroll.bind("<Configure>", app._schedule_movies_page_refresh)

    app.movies_grid_frame = CTkFrame(app.movies_scroll, fg_color="transparent")
    app.movies_grid_frame.pack(fill="both", expand=True)
    app.movies_grid_frame.pack_propagate(False)

    app.refresh_movies_page()
    app.after(120, app.refresh_movies_page)
    app.after(260, app.refresh_movies_page)