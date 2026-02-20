import json
from customtkinter import *
from tkinter import ttk
import os
from PIL import Image

class MovieApp(CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.geometry("1200x700")
        self.title("My Movie Collection")
        
        # Load and set background image
        self.set_background_image()
        
        # Data file
        self.data_file = "mydata.json"
        self.load_data()
        
        # Create a main frame with transparent background
        self.main_container = CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=(450,0), pady=0)
        
        self.tab_view = CTkTabview(self.main_container, width=850, height=500)
        self.tab_view.pack(pady=0, padx=(0,0), fill="both", expand=True)
        self.tab_view.add("Add Movie")
        self.tab_view.add("Movie List")
        
        # Setup each tab
        self.setup_add_movie_tab()
        self.setup_movie_list_tab()
    
    def set_background_image(self):
        """Set Joker image as background"""
        joker_path = os.path.join("assets", "joker1.jpg")
        
        if os.path.exists(joker_path):
            try:
                pil_image = Image.open(joker_path)
                pil_image = pil_image.resize((1200, 700), Image.Resampling.LANCZOS)
                
                self.bg_image = CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(1200, 700)
                )
                
                self.bg_label = CTkLabel(
                    self,
                    image=self.bg_image,
                    text=""
                )
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
                self.configure(fg_color="transparent")
               
            except Exception as e:
                self.configure(fg_color="#2b2b2b")
    def load_data(self):
        """Load movie data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.data = json.load(file)
    
    def save_data(self):
        """Save movie data to JSON file"""
        with open(self.data_file, "w") as file:
            json.dump(self.data, file, indent=4)
    
    def setup_add_movie_tab(self):
        """Setup the Add Movie tab with input fields"""
        tab = self.tab_view.tab("Add Movie")
        
        # Make tab slightly transparent
        tab.configure(fg_color="#2b2b2b")
    
        # Create frame for form
        form_frame = CTkFrame(tab, fg_color="transparent")
        form_frame.pack(pady=0, padx=0, fill="both", expand=True)
        
        # Movie Name
        CTkLabel(form_frame, text="Name:", font=("Arial", 14, "bold")).pack(anchor="w", padx=(170,0), pady=(100,0))
        self.name_entry = CTkEntry(form_frame, width=400,height=40, placeholder_text="Enter movie name", border_color="#000000", fg_color= "#4b4849", border_width=2)
        self.name_entry.pack(padx=0, pady=(0,15))
        
        # Genre
        CTkLabel(form_frame, text="Genre:", font=("Arial", 14, "bold")).pack(anchor="w", padx=(170,0), pady=(10,0))
        self.genre_entry = CTkEntry(form_frame, width=400,height=40, placeholder_text="Enter genre", border_color="#000000", fg_color= "#4b4849", border_width=2)
        self.genre_entry.pack(padx=0, pady=(0,15))
        
        # Actors
        CTkLabel(form_frame, text="Actors:", font=("Arial", 14, "bold")).pack(anchor="w", padx=(170,0), pady=(10,0))
        self.actors_entry = CTkEntry(form_frame, width=400,height=40, placeholder_text="Enter actors (comma separated)", border_color="#000000", fg_color= "#4b4849",    border_width=2)
        self.actors_entry.pack(padx=0, pady=(0,15))
        
        # Year of Release
        CTkLabel(form_frame, text="Year:", font=("Arial", 14, "bold")).pack(anchor="w", padx=(170,0), pady=(10,0))
        self.year_entry = CTkEntry(form_frame, width=400,height=40, placeholder_text="Enter year (e.g., 2023)", border_color="#000000", fg_color= "#4b4849", border_width=2  )
        self.year_entry.pack(padx=20, pady=(0,15))
        
        # Buttons frame
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        
        # Add button
        add_btn = CTkButton(
            button_frame, 
            text="Add Movie", 
            command=self.add_movie,
            width=150,
            height=40,
            font=("Arial", 14, "bold")
        )
        add_btn.pack(side="left", padx=10)
        
        # Clear button
        clear_btn = CTkButton(
            button_frame,
            text="Clear Fields",
            command=self.clear_fields,
            width=150,
            height=40,
            font=("Arial", 14),
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left", padx=10)
        
        # Status label
        self.status_label = CTkLabel(tab, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)
    
    def setup_movie_list_tab(self):
        """Setup the Movie List tab with a table"""
        tab = self.tab_view.tab("Movie List")
        
        # Create search bar
        self.search_bar = CTkEntry(
            tab, 
            width=400,
            height=40, 
            placeholder_text="Search movies...",
            border_color="#000000", 
            fg_color="#4b4849",    
            border_width=2
        )
        self.search_bar.pack(pady=(20,5))
        
        # Bind the search bar to update on every keystroke
        self.search_bar.bind("<KeyRelease>", self.apply_filter)
        
        # Create dropdown for search category
        self.drop_down = CTkOptionMenu(
            tab,
            values=["All Fields", "Name", "Genre", "Actors", "Year"],
            width=150,
            height=30,  # Increased height for better visibility
            fg_color="#4b4849",
            button_color="#8b0000",
            button_hover_color="#a52a2a",
            dropdown_fg_color="#333333",
            dropdown_hover_color="#8b0000",
            dropdown_text_color="white"
        )
        self.drop_down.pack(pady=(0,10))
        self.drop_down.set("All Fields")  # Set default value
        
        # Table frame
        table_frame = CTkFrame(tab)
        table_frame.pack(pady=(20,20), padx=20, fill="both", expand=True)
        
        # Create Treeview (table) with scrollbar
        columns = ("#", "Movie Name", "Genre", "Actors", "Year")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Define column headings
        self.tree.heading("#", text="#")
        self.tree.heading("Movie Name", text="Movie Name")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Actors", text="Actors")
        self.tree.heading("Year", text="Year")
        
        # Define column widths
        self.tree.column("#", width=50, anchor="center")
        self.tree.column("Movie Name", width=200)
        self.tree.column("Genre", width=150)
        self.tree.column("Actors", width=250)
        self.tree.column("Year", width=100, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        refresh_btn = CTkButton(
            tab,
            text="Refresh List",
            command=self.refresh_movie_list,
            width=150,
            height=35
        )
        refresh_btn.pack(pady=10)
        
        # Initial load
        self.refresh_movie_list()

    def apply_filter(self, event=None):
        """Apply filter to the table based on search bar and dropdown"""
        filter_text = self.search_bar.get().strip().lower()  # Use search_bar, not filter_entry
        search_field = self.drop_down.get()  # Get selected field from dropdown
        
        # Clear current table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not filter_text:
            # Show all movies
            for i, movie in enumerate(self.data["movies"], start=1):
                self.tree.insert("", "end", values=(
                    i,
                    movie.get("title", ""),
                    movie.get("genre", ""),
                    movie.get("actors", ""),
                    movie.get("year", "")
                ))
            return
        
        # Show only filtered movies based on selected field
        for i, movie in enumerate(self.data["movies"], start=1):
            match = False
            
            if search_field == "All Fields":
                if (filter_text in movie.get("title", "").lower() or
                    filter_text in movie.get("genre", "").lower() or
                    filter_text in movie.get("actors", "").lower() or
                    filter_text in movie.get("year", "").lower()):
                    match = True
            elif search_field == "Name":
                if filter_text in movie.get("title", "").lower():
                    match = True
            elif search_field == "Genre":
                if filter_text in movie.get("genre", "").lower():
                    match = True
            elif search_field == "Actors":
                if filter_text in movie.get("actors", "").lower():
                    match = True
            elif search_field == "Year":
                if filter_text in movie.get("year", "").lower():
                    match = True
            
            if match:
                self.tree.insert("", "end", values=(
                    i,
                    movie.get("title", ""),
                    movie.get("genre", ""),
                    movie.get("actors", ""),
                    movie.get("year", "")
                ))

    def refresh_movie_list(self):
        """Refresh the movie list table"""
        # Clear existing items
        for item in self.tree.get_children():   
            self.tree.delete(item)
        
        # Add all movies to table
        for i, movie in enumerate(self.data["movies"], start=1):
            self.tree.insert("", "end", values=(
                i,
                movie.get("title", ""),
                movie.get("genre", ""),
                movie.get("actors", ""),
                movie.get("year", "")
            ))
    
    
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
        
        # Create movie dictionary
        movie = {
            "title": name,
            "genre": genre,
            "actors": actors,
            "year": year
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
    
    def clear_fields(self):
        """Clear all input fields"""
        self.name_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.actors_entry.delete(0, END)
        self.year_entry.delete(0, END)
    
    def refresh_movie_list(self):
        """Refresh the movie list table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, movie in enumerate(self.data["movies"], start=1):
            self.tree.insert("", "end", values=(
                i,
                movie.get("title", ""),
                movie.get("genre", ""),
                movie.get("actors", ""),
                movie.get("year", "")
            ))

if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()