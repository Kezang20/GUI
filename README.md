# CineScope GUI

CineScope is a Tkinter movie discovery application powered by TMDB.

## Run

From this directory:

```powershell
python main.py
```

## Project structure

- `main.py` - application entry point and `CineScope` composition
- `about.py` - about screen
- `ui_layout.py` - window layout, navigation, scrolling, and shared UI helpers
- `home.py` - home screen and shared movie-loading helpers
- `catalog.py` - movie grids, cards, posters, search, and catalog filters
- `details.py` - movie details, cast, reviews, and streaming links
- `watchlist.py` - watchlist display and watchlist actions
- `account.py` - login and account creation screens
- `database.py` - SQLite persistence
- `tmdb.py` - TMDB API integration
- `config.py` - colors and genre definitions