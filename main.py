import tkinter as tk

from about import AboutMixin
import database
from account import AccountMixin
from catalog import CatalogMixin
from details import DetailsMixin
from home import HomeMixin
from ui_layout import LayoutMixin
from watchlist import WatchlistMixin


class CineScope(
    LayoutMixin,
    AboutMixin,
    HomeMixin,
    CatalogMixin,
    DetailsMixin,
    WatchlistMixin,
    AccountMixin,
    tk.Tk,
):

    def __init__(self):
        super().__init__()

        self.title("CineScope - Movie & TV Show Explorer")
        self.geometry("1400x850")
        self.minsize(1100, 700)
        self.configure(bg="#0b0f14")

        database.create_tables()
    

        self.current_user = None
        self.poster_cache = {}
        self.cast_cache = {}

        self.create_layout()
        self.show_home()


if __name__ == "__main__":
    app = CineScope()
    app.mainloop()
