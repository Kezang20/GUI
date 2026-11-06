import tkinter as tk
from tkinter import messagebox

import database
import tmdb
from config import ACCENT, ACCENT_HOVER, BG, CARD, MUTED, WHITE


class WatchlistMixin:

    def is_movie_saved(self, movie):

        if not self.current_user:
            return False

        movies = database.get_watchlist(
            self.current_user[0]
        )

        movie_id = movie.get("id")
        media_type = movie.get("media_type", "movie")

        for saved_movie in movies:

            if (
                saved_movie[0] == movie_id
                and (saved_movie[1] or "movie") == media_type
            ):
                return True

        return False

    # =====================================================
    # ADD TO WATCHLIST
    # =====================================================

    def add_watchlist(self, movie, button=None):

        if not self.current_user:

            messagebox.showwarning(
                "Login Required",
                "Please login before adding movies to your watchlist."
            )

            self.show_login()

            return


        if self.is_movie_saved(movie):

            if button:
                button.config(
                    text="❤️ Saved",
                    bg=ACCENT
                )

            return


        database.add_to_watchlist(
            self.current_user[0],
            movie
        )


        if button:

            button.config(
                text="❤️ Saved",
                bg=ACCENT
            )

            self.add_hover_effect(
                button,
                ACCENT,
                ACCENT_HOVER
            )


        messagebox.showinfo(
            "Watchlist",
            "Movie added to your watchlist!"
        )


    # =====================================================
    # REMOVE FROM WATCHLIST
    # =====================================================

    def remove_from_watchlist(
        self,
        movie_id,
        media_type
    ):

        if not self.current_user:

            messagebox.showwarning(
                "Login Required",
                "Please login to manage your watchlist."
            )

            return


        database.remove_from_watchlist(
            self.current_user[0],
            movie_id,
            media_type
        )


        self.show_watchlist()


    # =====================================================
    # WATCHLIST
    # =====================================================

    def show_watchlist(self):

        if not self.current_user:

            messagebox.showwarning(
                "Login Required",
                "Please login to view your watchlist."
            )

            self.show_login()

            return


        self.clear_content()


        title = tk.Label(
            self.content,
            text="❤️ My Watchlist",
            bg=BG,
            fg=WHITE,
            font=("Arial", 28, "bold")
        )

        title.pack(
            anchor="w",
            pady=20
        )


        movies = database.get_watchlist(
            self.current_user[0]
        )


        if not movies:

            tk.Label(
                self.content,
                text="Your watchlist is empty.",
                bg=BG,
                fg=MUTED,
                font=("Arial", 14)
            ).pack(
                pady=50
            )

            return


        grid = tk.Frame(
            self.content,
            bg=BG
        )

        grid.pack(
            fill="x"
        )


        for index, movie in enumerate(movies):

            movie_dict = {
                "id": movie[0],
                "media_type": movie[1] or "movie",
                "title": movie[2],
                "poster_path": movie[3],
                "overview": movie[4],
                "release_date": movie[5]
            }


            card = self.create_movie_card(
                grid,
                movie_dict,
                watchlist_card=True
            )


            card.grid(
                row=index // 3,
                column=index % 3,
                padx=10,
                pady=10,
                sticky="nsew"
            )


        for column in range(3):

            grid.columnconfigure(
                column,
                weight=1
            )


    # =====================================================
    # HIDDEN GEMS
    # =====================================================

    def show_hidden(self):

        self.clear_content()


        title = tk.Label(
            self.content,
            text="💎 Hidden Gems",
            bg=BG,
            fg=WHITE,
            font=("Arial", 28, "bold")
        )

        title.pack(
            anchor="w",
            pady=20
        )


        movies = self.get_movies(
            tmdb.hidden_gems,
            limit=12
        )


        self.create_movie_grid(
            movies
        )
