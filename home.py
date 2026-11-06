import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps, ImageTk
import tmdb
from config import BG, CARD, MUTED, WHITE


class HomeMixin:

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


        hero = tk.Canvas(
            self.content,
            bg="#050505",
            height=220
        )

        hero.pack(
            fill="x",
            pady=(0, 30)
        )

        hero.pack_propagate(False)

        hero.update_idletasks()
        hero_image = self._load_hero_image(hero)
        if hero_image:
            hero.image = hero_image
            hero.create_image(
                0,
                0,
                image=hero_image,
                anchor="nw"
            )

        center_x = max(hero.winfo_width(), 800) // 2
        hero.create_text(
            center_x + 2,
            91,
            text="🎬 Your World of Cinema",
            fill="#000000",
            font=("Arial", 28, "bold")
        )
        hero.create_text(
            center_x,
            89,
            text="🎬 Your World of Cinema",
            fill=WHITE,
            font=("Arial", 28, "bold")
        )
        hero.create_text(
            center_x + 1,
            132,
            text="Search, discover and save your favorite movies.",
            fill="#000000",
            font=("Arial", 13)
        )
        hero.create_text(
            center_x,
            130,
            text="Search, discover and save your favorite movies.",
            fill=WHITE,
            font=("Arial", 13)
        )


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

    def _load_hero_image(self, hero):
        image_path = Path(__file__).parent / "assets" / "vintage-filmstrip-texture.jpg"

        try:
            hero.update_idletasks()
            width = max(hero.winfo_width(), 800)
            image = Image.open(image_path).convert("RGB")
            image = ImageOps.fit(
                image,
                (width, 220),
                method=Image.Resampling.LANCZOS
            )
            image = ImageEnhance.Brightness(image).enhance(0.62)
            return ImageTk.PhotoImage(image)
        except (FileNotFoundError, OSError):
            return None


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


