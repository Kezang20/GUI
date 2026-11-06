import tkinter as tk
from tkinter import messagebox

from io import BytesIO
import threading

from PIL import Image, ImageTk
import requests

import tmdb
import database
from config import (
    ACCENT,
    ACCENT_HOVER,
    BG,
    CARD,
    CARD_HOVER,
    GENRES,
    MUTED,
    WHITE,
)


class CatalogMixin:

    def create_movie_grid(self, movies):

        if not movies:

            label = tk.Label(
                self.content,
                text="No movies available.",
                bg=BG,
                fg=MUTED,
                font=("Arial", 13)
            )

            label.pack(
                pady=30
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

            row = index // 3
            column = index % 3


            card = self.create_movie_card(
                grid,
                movie
            )


            card.grid(
                row=row,
                column=column,
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
    # MOVIE CARD
    # =====================================================

    def create_movie_card(
        self,
        parent,
        movie,
        watchlist_card=False
    ):

        card = tk.Frame(
            parent,
            bg=CARD,
            width=280,
            height=360
        )

        card.pack_propagate(False)


        poster_label = tk.Label(
            card,
            bg=CARD
        )

        poster_label.pack(
            pady=10
        )


        poster_path = movie.get(
            "poster_path"
        )


        if poster_path:

            self.load_poster(
                poster_label,
                poster_path
            )

        else:

            poster_label.config(
                text="No Poster",
                fg=MUTED,
                font=("Arial", 12)
            )


        title = (
            movie.get("title")
            or movie.get("name")
            or "Unknown"
        )


        title_label = tk.Label(
            card,
            text=title,
            bg=CARD,
            fg=WHITE,
            font=("Arial", 13, "bold"),
            wraplength=240
        )

        title_label.pack(
            padx=10,
            pady=5
        )


        rating = movie.get(
            "vote_average",
            0
        ) or 0


        rating_label = tk.Label(
            card,
            text=f"⭐ {float(rating):.1f}",
            bg=CARD,
            fg="#ffd700",
            font=("Arial", 11)
        )

        rating_label.pack()


        button_frame = tk.Frame(
            card,
            bg=CARD
        )

        button_frame.pack(
            pady=10
        )


        details_button = tk.Button(
            button_frame,
            text="Details",
            command=lambda m=movie: self.show_details(m),
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2"
        )

        details_button.pack(
            side="left",
            padx=5
        )

        self.add_hover_effect(
            details_button,
            ACCENT,
            ACCENT_HOVER
        )


        if watchlist_card:

            remove_button = tk.Button(
                button_frame,
                text="🗑 Remove",
                command=lambda m=movie: self.remove_from_watchlist(
                    m["id"],
                    m.get("media_type", "movie")
                ),
                bg="#333b45",
                fg=WHITE,
                activebackground="#4a535e",
                activeforeground=WHITE,
                relief="flat",
                cursor="hand2"
            )

            remove_button.pack(
                side="left",
                padx=5
            )

            self.add_hover_effect(
                remove_button,
                "#333b45",
                "#4a535e"
            )

        else:

            saved = self.is_movie_saved(movie)

            if saved:
                button_text = "❤️ Saved"
                button_bg = ACCENT
            else:
                button_text = "♡ Save"
                button_bg = "#252f3b"

            watch_button = tk.Button(
                button_frame,
                text=button_text,
                command=lambda m=movie, b=None: self.add_watchlist(
                    m,
                    watch_button
                ),
                bg=button_bg,
                fg=WHITE,
                activebackground=ACCENT_HOVER,
                activeforeground=WHITE,
                relief="flat",
                cursor="hand2"
            )

            watch_button.pack(
                side="left",
                padx=5
            )

            if saved:
                self.add_hover_effect(
                    watch_button,
                    ACCENT,
                    ACCENT_HOVER
                )
            else:
                self.add_hover_effect(
                    watch_button,
                    "#252f3b",
                    CARD_HOVER
                )


        return card


    # =====================================================
    # LOAD POSTER
    # =====================================================

    def load_poster(
        self,
        label,
        poster_path
    ):

        if not poster_path:
            return


        if poster_path in self.poster_cache:

            photo = self.poster_cache[
                poster_path
            ]

            label.configure(
                image=photo,
                text=""
            )

            label.image = photo

            return


        def download_poster():

            try:

                url = (
                    tmdb.IMAGE_URL
                    + poster_path
                )

                response = requests.get(
                    url,
                    timeout=10
                )

                response.raise_for_status()


                image = Image.open(
                    BytesIO(response.content)
                ).convert("RGB")


                image = image.resize(
                    (150, 210),
                    Image.Resampling.LANCZOS
                )


                photo = ImageTk.PhotoImage(
                    image
                )


                self.after(
                    0,
                    self._set_poster,
                    label,
                    poster_path,
                    photo
                )


            except Exception:

                self.after(
                    0,
                    self._poster_failed,
                    label
                )


        threading.Thread(
            target=download_poster,
            daemon=True
        ).start()


    def _set_poster(
        self,
        label,
        poster_path,
        photo
    ):

        if label.winfo_exists():

            self.poster_cache[
                poster_path
            ] = photo

            label.configure(
                image=photo,
                text=""
            )

            label.image = photo


    def _poster_failed(self, label):

        if label.winfo_exists():

            label.configure(
                text="No Poster",
                fg=MUTED,
                font=("Arial", 12)
            )


    # =====================================================
    # SEARCH
    # =====================================================

    def search(self):

        query = self.search_entry.get().strip()


        if (
            not query
            or query == "Search movies and TV shows..."
        ):

            messagebox.showwarning(
                "Search",
                "Please enter a movie or TV show name."
            )

            return


        self.clear_content()


        title = tk.Label(
            self.content,
            text=f'Search Results for "{query}"',
            bg=BG,
            fg=WHITE,
            font=("Arial", 25, "bold")
        )

        title.pack(
            anchor="w",
            pady=(10, 20)
        )


        movies = self.get_movies(
            lambda: tmdb.search_movies(query),
            limit=12
        )


        self.create_movie_grid(
            movies
        )


    # =====================================================
    # TRENDING
    # =====================================================

    def show_trending(self):

        self.clear_content()


        title = tk.Label(
            self.content,
            text="🔥 Trending Movies",
            bg=BG,
            fg=WHITE,
            font=("Arial", 28, "bold")
        )

        title.pack(
            anchor="w",
            pady=20
        )


        movies = self.get_movies(
            tmdb.trending_movies,
            limit=12
        )


        self.create_movie_grid(
            movies
        )


    # =====================================================
    # GENRE FILTER
    # =====================================================

    def filter_genre(self, event=None):

        selected_genre = self.genre_var.get()

        genre_id = GENRES.get(
            selected_genre
        )


        self.clear_content()


        title = tk.Label(
            self.content,
            text=f"🎬 {selected_genre}",
            bg=BG,
            fg=WHITE,
            font=("Arial", 28, "bold")
        )

        title.pack(
            anchor="w",
            pady=(10, 20)
        )


        loading = tk.Label(
            self.content,
            text=f"Loading {selected_genre} movies...",
            bg=BG,
            fg=MUTED,
            font=("Arial", 13)
        )

        loading.pack(
            pady=30
        )


        self.update_idletasks()


        try:

            if genre_id is None:

                movies = tmdb.trending_movies()

            else:

                movies = tmdb.movies_by_genre(
                    genre_id
                )


            loading.destroy()


            self.create_movie_grid(
                movies[:12]
            )


            self.canvas.yview_moveto(0)


        except Exception as error:

            loading.destroy()

            messagebox.showerror(
                "Genre Error",
                str(error)
            )


    # =====================================================
    # TOP RATED
    # =====================================================

    def show_top_rated(self):

        self.clear_content()


        title = tk.Label(
            self.content,
            text="⭐ Top Rated Movies",
            bg=BG,
            fg=WHITE,
            font=("Arial", 28, "bold")
        )

        title.pack(
            anchor="w",
            pady=20
        )


        movies = self.get_movies(
            tmdb.top_rated_movies,
            limit=12
        )


        self.create_movie_grid(
            movies
        )
