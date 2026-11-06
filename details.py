import tkinter as tk
from tkinter import messagebox
from io import BytesIO
import threading
import webbrowser
from urllib.parse import quote

from PIL import Image, ImageTk
import requests

import tmdb
from config import ACCENT, ACCENT_HOVER, BG, CARD, CARD_HOVER, MUTED, TEXT, WHITE


class DetailsMixin:

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

        saved = self.is_movie_saved(movie)

        if saved:
            watchlist_text = "❤️ Saved"
            watchlist_bg = ACCENT
        else:
            watchlist_text = "♡ Add to Watchlist"
            watchlist_bg = "#252f3b"


        watchlist_button = tk.Button(
            info,
            text=watchlist_text,
            command=lambda: self.add_watchlist(
                movie,
                watchlist_button
            ),
            bg=watchlist_bg,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        )

        watchlist_button.pack(
            anchor="w",
            pady=(20, 10),
            ipadx=10,
            ipady=8
        )


        if saved:

            self.add_hover_effect(
                watchlist_button,
                ACCENT,
                ACCENT_HOVER
            )

        else:

            self.add_hover_effect(
                watchlist_button,
                "#252f3b",
                CARD_HOVER
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
