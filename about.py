import tkinter as tk
from config import BG, CARD, TEXT, WHITE


class AboutMixin:
    def show_about(self):
        self.clear_content()

        title = tk.Label(
            self.content,
            text="About CineScope",
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )
        title.pack(
            anchor="w",
            pady=(20, 10)
        )

        text = """
CineScope is an interactive movie discovery application.

The application allows users to:

• Discover trending movies
• Browse top-rated movies
• Search movies and TV shows
• Filter movies by genre
• View detailed movie information
• View ratings and genres
• View user reviews
• View movie cast
• Manage a personal watchlist
• Discover hidden gems

Movie information is provided through The Movie Database (TMDB).

CineScope was developed as a collaborative project.
"""

        tk.Label(
            self.content,
            text=text,
            bg=CARD,
            fg=TEXT,
            justify="left",
            anchor="nw",
            font=("Arial", 13),
            padx=30,
            pady=30
        ).pack(
            fill="x",
            pady=20
        )