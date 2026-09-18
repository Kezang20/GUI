import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk

import requests
from io import BytesIO

import threading
import webbrowser
from urllib.parse import quote

import database
import tmdb


# =========================================================
# COLORS
# =========================================================

BG = "#0b0f14"
SIDEBAR = "#111820"
CARD = "#161e27"
CARD_HOVER = "#202b37"

WHITE = "#ffffff"
TEXT = "#e7eef6"
MUTED = "#9aa7b5"

ACCENT = "#e50914"
ACCENT_HOVER = "#ff1f2d"


# =========================================================
# GENRES
# =========================================================

GENRES = {
    "All Genres": None,
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "History": 36,
    "Horror": 27,
    "Music": 10402,
    "Mystery": 9648,
    "Romance": 10749,
    "Science Fiction": 878,
    "TV Movie": 10770,
    "Thriller": 53,
    "War": 10752,
    "Western": 37
}


# =========================================================
# APP
# =========================================================

class CineScope(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("CineScope - Movie & TV Show Explorer")
        self.geometry("1400x850")
        self.minsize(1100, 700)
        self.configure(bg=BG)

        database.create_tables()

        self.current_user = None
        self.poster_cache = {}
        self.cast_cache = {}

        self.create_layout()
        self.show_home()


    # =====================================================
    # MAIN LAYOUT
    # =====================================================

    def create_layout(self):

        # -------------------------------------------------
        # SIDEBAR
        # -------------------------------------------------

        self.sidebar = tk.Frame(
            self,
            bg=SIDEBAR,
            width=240
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        logo = tk.Label(
            self.sidebar,
            text="🎬 CineScope",
            font=("Arial", 22, "bold"),
            bg=SIDEBAR,
            fg=WHITE
        )

        logo.pack(
            pady=(35, 45)
        )

        self.nav_button(
            "🏠  Home",
            self.show_home
        )

        self.nav_button(
            "🔥  Trending",
            self.show_trending
        )

        self.nav_button(
            "⭐  Top Rated",
            self.show_top_rated
        )

        self.nav_button(
            "❤️  My Watchlist",
            self.show_watchlist
        )

        self.nav_button(
            "💎  Hidden Gems",
            self.show_hidden
        )

        self.nav_button(
            "ℹ️  About",
            self.show_about
        )

        self.login_button = tk.Button(
            self.sidebar,
            text="🔐  Log In",
            command=self.show_login,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 12, "bold"),
            cursor="hand2"
        )

        self.login_button.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20,
            ipady=10
        )


        # -------------------------------------------------
        # MAIN AREA
        # -------------------------------------------------

        self.main = tk.Frame(
            self,
            bg=BG
        )

        self.main.pack(
            side="right",
            fill="both",
            expand=True
        )


        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        self.header = tk.Frame(
            self.main,
            bg=BG,
            height=80
        )

        self.header.pack(
            fill="x",
            padx=30,
            pady=20
        )

        self.header.pack_propagate(False)


        # Search box

        self.search_entry = tk.Entry(
            self.header,
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 13)
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=12,
            padx=(0, 10)
        )

        self.search_entry.insert(
            0,
            "Search movies and TV shows..."
        )

        self.search_entry.bind(
            "<FocusIn>",
            self.clear_search_placeholder
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search()
        )


        # Search button

        self.search_button = tk.Button(
            self.header,
            text="🔍 Search",
            command=self.search,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        )

        self.search_button.pack(
            side="right",
            padx=5,
            ipadx=15,
            ipady=8
        )


        # Genre dropdown

        self.genre_var = tk.StringVar()

        self.genre_dropdown = ttk.Combobox(
            self.header,
            textvariable=self.genre_var,
            state="readonly",
            width=20,
            font=("Arial", 11)
        )

        self.genre_dropdown["values"] = list(
            GENRES.keys()
        )

        self.genre_dropdown.current(0)

        self.genre_dropdown.pack(
            side="right",
            padx=10,
            ipady=5
        )

        self.genre_dropdown.bind(
            "<<ComboboxSelected>>",
            self.filter_genre
        )


        # -------------------------------------------------
        # SCROLLABLE CONTENT AREA
        # -------------------------------------------------

        self.content_container = tk.Frame(
            self.main,
            bg=BG
        )

        self.content_container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 20)
        )


        self.canvas = tk.Canvas(
            self.content_container,
            bg=BG,
            highlightthickness=0
        )

        self.scrollbar = ttk.Scrollbar(
            self.content_container,
            orient="vertical",
            command=self.canvas.yview
        )


        self.content = tk.Frame(
            self.canvas,
            bg=BG
        )


        self.content_window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )


        self.content.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_content
        )


        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )


        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )


        # Mouse wheel scrolling

        self.canvas.bind_all(
            "<MouseWheel>",
            self.mouse_scroll
        )

        self.canvas.bind_all(
            "<Button-4>",
            self.mouse_scroll_linux
        )

        self.canvas.bind_all(
            "<Button-5>",
            self.mouse_scroll_linux
        )


    # =====================================================
    # NAVIGATION BUTTON
    # =====================================================

    def nav_button(self, text, command):

        button = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            anchor="w",
            bg=SIDEBAR,
            fg=TEXT,
            activebackground=CARD_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 12),
            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=15,
            pady=4,
            ipady=10
        )


    # =====================================================
    # SCROLLING
    # =====================================================

    def update_scroll_region(self, event=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )


    def resize_content(self, event):
        self.canvas.itemconfig(
            self.content_window,
            width=event.width
        )


    def mouse_scroll(self, event):

        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )


    def mouse_scroll_linux(self, event):

        if event.num == 4:
            self.canvas.yview_scroll(
                -3,
                "units"
            )

        elif event.num == 5:
            self.canvas.yview_scroll(
                3,
                "units"
            )


    def reset_scroll(self):
        self.canvas.yview_moveto(0)


    # =====================================================
    # CLEAR CONTENT
    # =====================================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

        self.reset_scroll()


    # =====================================================
    # SEARCH PLACEHOLDER
    # =====================================================

    def clear_search_placeholder(self, event=None):

        if self.search_entry.get() == "Search movies and TV shows...":
            self.search_entry.delete(
                0,
                "end"
            )


    # =====================================================
    # HOME
    # =====================================================

    def show_home(self):

        self.clear_content()


        title = tk.Label(
            self.content,
            text="Welcome to CineScope",
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )

        title.pack(
            anchor="w",
            pady=(10, 5)
        )


        subtitle = tk.Label(
            self.content,
            text="Discover trending movies and top-rated films.",
            bg=BG,
            fg=MUTED,
            font=("Arial", 13)
        )

        subtitle.pack(
            anchor="w",
            pady=(0, 20)
        )


        hero = tk.Frame(
            self.content,
            bg=CARD,
            height=220
        )

        hero.pack(
            fill="x",
            pady=(0, 30)
        )

        hero.pack_propagate(False)


        hero_title = tk.Label(
            hero,
            text="🎬 Your World of Cinema",
            bg=CARD,
            fg=WHITE,
            font=("Arial", 28, "bold")
        )

        hero_title.pack(
            pady=(50, 10)
        )


        hero_text = tk.Label(
            hero,
            text="Search, discover and save your favorite movies.",
            bg=CARD,
            fg=MUTED,
            font=("Arial", 13)
        )

        hero_text.pack()


        self.section_title(
            "🔥 Trending Now"
        )

        trending = self.get_movies(
            tmdb.trending_movies,
            limit=6
        )

        self.create_movie_grid(
            trending
        )


        self.section_title(
            "⭐ Top Rated"
        )

        top = self.get_movies(
            tmdb.top_rated_movies,
            limit=6
        )

        self.create_movie_grid(
            top
        )


    # =====================================================
    # SECTION TITLE
    # =====================================================

    def section_title(self, text):

        label = tk.Label(
            self.content,
            text=text,
            bg=BG,
            fg=WHITE,
            font=("Arial", 20, "bold")
        )

        label.pack(
            anchor="w",
            pady=(20, 15)
        )


    # =====================================================
    # GET MOVIES
    # =====================================================

    def get_movies(self, function, limit=6):

        try:

            movies = function()

            return movies[:limit]

        except Exception as error:

            messagebox.showerror(
                "TMDB Error",
                str(error)
            )

            return []


    # =====================================================
    # MOVIE GRID
    # =====================================================

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

        else:

            watch_button = tk.Button(
                button_frame,
                text="❤️ Save",
                command=lambda m=movie: self.add_watchlist(m),
                bg="#252f3b",
                fg=WHITE,
                activebackground=CARD_HOVER,
                activeforeground=WHITE,
                relief="flat",
                cursor="hand2"
            )

            watch_button.pack(
                side="left",
                padx=5
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


    # =====================================================
    # MOVIE DETAILS
    # =====================================================

    def show_details(self, movie):

        self.clear_content()


        movie_id = movie["id"]

        media_type = movie.get(
            "media_type",
            "movie"
        )


        try:

            data = tmdb.movie_details(
                movie_id,
                media_type
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

            return


        title = (
            data.get("title")
            or data.get("name")
            or "Unknown"
        )


        heading = tk.Label(
            self.content,
            text=title,
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )

        heading.pack(
            anchor="w",
            pady=10
        )


        details = tk.Frame(
            self.content,
            bg=CARD
        )

        details.pack(
            fill="x",
            pady=20
        )


        poster = tk.Label(
            details,
            bg=CARD
        )

        poster.pack(
            side="left",
            padx=25,
            pady=25
        )


        if data.get("poster_path"):

            self.load_poster(
                poster,
                data["poster_path"]
            )


        info = tk.Frame(
            details,
            bg=CARD
        )

        info.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20,
            pady=25
        )


        release = (
            data.get("release_date")
            or data.get("first_air_date")
            or "Unknown"
        )


        rating = data.get(
            "vote_average",
            0
        ) or 0


        genres = ", ".join(
            g["name"]
            for g in data.get(
                "genres",
                []
            )
        )


        runtime = data.get(
            "runtime",
            "Unknown"
        )


        tk.Label(
            info,
            text=f"Release: {release}",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 12)
        ).pack(
            anchor="w",
            pady=5
        )


        tk.Label(
            info,
            text=f"Rating: ⭐ {float(rating):.1f}",
            bg=CARD,
            fg="#ffd700",
            font=("Arial", 12)
        ).pack(
            anchor="w",
            pady=5
        )


        tk.Label(
            info,
            text=f"Genres: {genres}",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 12)
        ).pack(
            anchor="w",
            pady=5
        )


        tk.Label(
            info,
            text=f"Runtime: {runtime} minutes",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 12)
        ).pack(
            anchor="w",
            pady=5
        )


        tk.Label(
            info,
            text="Overview",
            bg=CARD,
            fg=WHITE,
            font=("Arial", 16, "bold")
        ).pack(
            anchor="w",
            pady=(20, 5)
        )


        overview = tk.Label(
            info,
            text=data.get(
                "overview",
                "No description available."
            ),
            bg=CARD,
            fg=MUTED,
            wraplength=650,
            justify="left",
            font=("Arial", 11)
        )

        overview.pack(
            anchor="w"
        )


        # -------------------------------------------------
        # WATCHLIST BUTTON
        # -------------------------------------------------

        tk.Button(
            info,
            text="❤️ Add to Watchlist",
            command=lambda: self.add_watchlist(movie),
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(
            anchor="w",
            pady=(20, 10),
            ipadx=10,
            ipady=8
        )


        # =================================================
        # USER REVIEWS
        # =================================================

        reviews = data.get(
            "reviews",
            {}
        ).get(
            "results",
            []
        )[:5]


        tk.Label(
            self.content,
            text="⭐ User Reviews",
            bg=BG,
            fg=WHITE,
            font=("Arial", 20, "bold")
        ).pack(
            anchor="w",
            pady=(15, 10)
        )


        if reviews:

            for review in reviews:

                review_card = tk.Frame(
                    self.content,
                    bg=CARD
                )

                review_card.pack(
                    fill="x",
                    pady=(0, 12)
                )


                author = review.get(
                    "author",
                    "Anonymous"
                )


                author_details = (
                    review.get(
                        "author_details"
                    )
                    or {}
                )


                user_rating = author_details.get(
                    "rating"
                )


                if user_rating is not None:

                    rating_text = (
                        f"⭐ {user_rating}/10"
                    )

                else:

                    rating_text = "No rating"


                tk.Label(
                    review_card,
                    text=f"{author}  •  {rating_text}",
                    bg=CARD,
                    fg=WHITE,
                    font=("Arial", 11, "bold")
                ).pack(
                    anchor="w",
                    padx=15,
                    pady=(12, 5)
                )


                review_text = review.get(
                    "content",
                    "No review text available."
                ).strip()


                tk.Label(
                    review_card,
                    text=review_text,
                    bg=CARD,
                    fg=MUTED,
                    wraplength=850,
                    justify="left",
                    font=("Arial", 10)
                ).pack(
                    anchor="w",
                    padx=15,
                    pady=(0, 12)
                )


        else:

            tk.Label(
                self.content,
                text="No user reviews available for this title.",
                bg=BG,
                fg=MUTED,
                font=("Arial", 11)
            ).pack(
                anchor="w",
                pady=(0, 20)
            )


        # =================================================
        # WATCH / STREAMING BUTTONS
        # =================================================

        watch_frame = tk.Frame(
            info,
            bg=CARD
        )

        watch_frame.pack(
            anchor="w",
            pady=(0, 10)
        )


        tk.Button(
            watch_frame,
            text="▶ Watch on Netflix",
            command=lambda: self.watch_on_netflix(title),
            bg="#e50914",
            fg=WHITE,
            activebackground="#b20710",
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(
            side="left",
            padx=(0, 10),
            ipadx=10,
            ipady=8
        )


        tk.Button(
            watch_frame,
            text="🔎 Where to Watch",
            command=lambda: self.find_where_to_watch(title),
            bg="#252f3b",
            fg=WHITE,
            activebackground=CARD_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(
            side="left",
            ipadx=10,
            ipady=8
        )


        # =================================================
        # CAST
        # =================================================

        cast = data.get(
            "credits",
            {}
        ).get(
            "cast",
            []
        )[:6]


        if cast:

            tk.Label(
                self.content,
                text="🎭 Cast",
                bg=BG,
                fg=WHITE,
                font=("Arial", 20, "bold")
            ).pack(
                anchor="w",
                pady=(15, 10)
            )


            cast_frame = tk.Frame(
                self.content,
                bg=BG
            )

            cast_frame.pack(
                fill="x",
                pady=(0, 20)
            )


            for actor in cast:

                actor_card = tk.Frame(
                    cast_frame,
                    bg=CARD,
                    width=135,
                    height=205
                )

                actor_card.pack(
                    side="left",
                    padx=(0, 12),
                    pady=5
                )

                actor_card.pack_propagate(False)


                profile = tk.Label(
                    actor_card,
                    bg=CARD,
                    fg=MUTED,
                    text="No Photo",
                    font=("Arial", 9)
                )

                profile.pack(
                    pady=(8, 5)
                )


                profile_path = actor.get(
                    "profile_path"
                )


                if profile_path:

                    self.load_cast_photo(
                        profile,
                        profile_path
                    )


                actor_name = actor.get(
                    "name",
                    "Unknown"
                )


                tk.Label(
                    actor_card,
                    text=actor_name,
                    bg=CARD,
                    fg=WHITE,
                    font=("Arial", 10, "bold"),
                    wraplength=115,
                    justify="center"
                ).pack(
                    padx=5,
                    pady=(2, 2)
                )


                character = actor.get(
                    "character"
                )


                if character:

                    tk.Label(
                        actor_card,
                        text=f"as {character}",
                        bg=CARD,
                        fg=MUTED,
                        font=("Arial", 8),
                        wraplength=115,
                        justify="center"
                    ).pack(
                        padx=5
                    )


    # =====================================================
    # LOAD CAST PHOTO
    # =====================================================

    def load_cast_photo(
        self,
        label,
        profile_path
    ):

        if not profile_path:
            return


        if profile_path in self.cast_cache:

            photo = self.cast_cache[
                profile_path
            ]

            label.configure(
                image=photo,
                text=""
            )

            label.image = photo

            return


        def download_cast_photo():

            try:

                url = (
                    tmdb.IMAGE_URL
                    + profile_path
                )


                response = requests.get(
                    url,
                    timeout=10
                )

                response.raise_for_status()


                image = Image.open(
                    BytesIO(response.content)
                ).convert("RGB")


                image.thumbnail(
                    (115, 150),
                    Image.Resampling.LANCZOS
                )


                self.after(
                    0,
                    self._set_cast_photo,
                    label,
                    profile_path,
                    image
                )


            except Exception:

                self.after(
                    0,
                    self._cast_photo_failed,
                    label
                )


        threading.Thread(
            target=download_cast_photo,
            daemon=True
        ).start()


    def _set_cast_photo(
        self,
        label,
        profile_path,
        image
    ):

        if not label.winfo_exists():
            return


        photo = ImageTk.PhotoImage(
            image
        )


        self.cast_cache[
            profile_path
        ] = photo


        label.configure(
            image=photo,
            text=""
        )

        label.image = photo


    def _cast_photo_failed(self, label):

        if label.winfo_exists():

            label.configure(
                text="No Photo",
                fg=MUTED,
                font=("Arial", 9)
            )


    # =====================================================
    # WATCH LINKS
    # =====================================================

    def watch_on_netflix(self, title):

        url = (
            "https://www.netflix.com/search?q="
            + quote(title)
        )

        webbrowser.open(url)


    def find_where_to_watch(self, title):

        url = (
            "https://www.justwatch.com/us/search?q="
            + quote(title)
        )

        webbrowser.open(url)


    # =====================================================
    # ADD TO WATCHLIST
    # =====================================================

    def add_watchlist(self, movie):

        if not self.current_user:

            messagebox.showwarning(
                "Login Required",
                "Please login before adding movies to your watchlist."
            )

            self.show_login()

            return


        database.add_to_watchlist(
            self.current_user[0],
            movie
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


    # =====================================================
    # ABOUT
    # =====================================================

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


    # =====================================================
    # LOGIN
    # =====================================================

    def show_login(self):

        self.clear_content()


        title = tk.Label(
            self.content,
            text="🔐 Login",
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )

        title.pack(
            pady=(50, 30)
        )


        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=40,
            pady=40
        )

        form.pack(
            ipadx=100
        )


        tk.Label(
            form,
            text="Email",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11)
        ).pack(
            anchor="w"
        )


        email = tk.Entry(
            form,
            bg="#202832",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 12)
        )

        email.pack(
            fill="x",
            pady=(5, 20),
            ipady=8
        )


        tk.Label(
            form,
            text="Password",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11)
        ).pack(
            anchor="w"
        )


        password = tk.Entry(
            form,
            show="*",
            bg="#202832",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 12)
        )

        password.pack(
            fill="x",
            pady=(5, 20),
            ipady=8
        )


        def login():

            user = database.login_user(
                email.get(),
                password.get()
            )


            if user:

                self.current_user = user


                self.login_button.config(
                    text=f"👤 {user[1]}"
                )


                messagebox.showinfo(
                    "Login",
                    f"Welcome back, {user[1]}!"
                )


                self.show_home()


            else:

                messagebox.showerror(
                    "Login Failed",
                    "Incorrect email or password."
                )


        tk.Button(
            form,
            text="Log In",
            command=login,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(
            fill="x",
            pady=10,
            ipady=8
        )


        tk.Button(
            form,
            text="Create Account",
            command=self.show_signup,
            bg="#252f3b",
            fg=WHITE,
            activebackground=CARD_HOVER,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2"
        ).pack(
            fill="x",
            ipady=8
        )


    # =====================================================
    # SIGNUP
    # =====================================================

    def show_signup(self):

        self.clear_content()


        title = tk.Label(
            self.content,
            text="Create Account",
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )

        title.pack(
            pady=30
        )


        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=40,
            pady=40
        )

        form.pack(
            ipadx=100
        )


        entries = {}


        fields = [
            ("Full Name", "name"),
            ("Email", "email"),
            ("Password", "password")
        ]


        for label_text, key in fields:

            tk.Label(
                form,
                text=label_text,
                bg=CARD,
                fg=TEXT,
                font=("Arial", 11)
            ).pack(
                anchor="w"
            )


            entry = tk.Entry(
                form,
                bg="#202832",
                fg=WHITE,
                insertbackground=WHITE,
                relief="flat",
                font=("Arial", 12)
            )


            if key == "password":

                entry.config(
                    show="*"
                )


            entry.pack(
                fill="x",
                pady=(5, 15),
                ipady=8
            )


            entries[key] = entry


        def signup():

            name = entries[
                "name"
            ].get().strip()


            email = entries[
                "email"
            ].get().strip()


            password = entries[
                "password"
            ].get()


            if (
                not name
                or not email
                or not password
            ):

                messagebox.showwarning(
                    "Signup",
                    "Please fill all fields."
                )

                return


            success = database.create_user(
                name,
                email,
                password
            )


            if success:

                messagebox.showinfo(
                    "Success",
                    "Account created successfully!"
                )

                self.show_login()


            else:

                messagebox.showerror(
                    "Signup Failed",
                    "An account with this email already exists."
                )


        tk.Button(
            form,
            text="Create Account",
            command=signup,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(
            fill="x",
            ipady=8
        )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app = CineScope()

    app.mainloop()