import tkinter as tk
from tkinter import ttk

from config import (
    ACCENT,
    ACCENT_HOVER,
    BG,
    CARD,
    CARD_HOVER,
    GENRES,
    SIDEBAR,
    TEXT,
    WHITE,
)


class LayoutMixin:

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

        self.add_hover_effect(
            button,
            SIDEBAR,
            CARD_HOVER
        )


    # =====================================================
    # BUTTON HOVER EFFECT
    # =====================================================

    def add_hover_effect(self, button, normal_bg, hover_bg):

        button.bind(
            "<Enter>",
            lambda event: button.config(bg=hover_bg)
        )

        button.bind(
            "<Leave>",
            lambda event: button.config(bg=normal_bg)
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
