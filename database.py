import sqlite3
import hashlib


DB_NAME = "cinescope.db"


# -----------------------------
# Database connection
# -----------------------------

def connect():
    return sqlite3.connect(DB_NAME)


# -----------------------------
# Create database tables
# -----------------------------

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Watchlist table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            media_type TEXT,
            title TEXT,
            poster_path TEXT,
            overview TEXT,
            release_date TEXT,
            watched INTEGER DEFAULT 0,
            UNIQUE(user_id, movie_id, media_type),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Password hashing
# -----------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -----------------------------
# Create user
# -----------------------------

def create_user(name, email, password):
    try:
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (
            name,
            email,
            hash_password(password)
        ))

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:
        return False


# -----------------------------
# Login user
# -----------------------------

def login_user(email, password):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE email = ? AND password = ?
    """, (
        email,
        hash_password(password)
    ))

    user = cursor.fetchone()

    conn.close()

    return user


# -----------------------------
# Add movie/TV show to watchlist
# -----------------------------

def add_to_watchlist(user_id, movie):
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO watchlist
            (
                user_id,
                movie_id,
                media_type,
                title,
                poster_path,
                overview,
                release_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            movie["id"],
            movie.get("media_type", "movie"),
            movie.get("title") or movie.get("name"),
            movie.get("poster_path"),
            movie.get("overview", ""),
            movie.get("release_date")
            or movie.get("first_air_date", "")
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        # Movie is already in the watchlist
        pass

    conn.close()


# -----------------------------
# Remove movie/TV show
# from watchlist
# -----------------------------

def remove_from_watchlist(user_id, movie_id, media_type):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM watchlist
        WHERE user_id = ?
        AND movie_id = ?
        AND media_type = ?
    """, (
        user_id,
        movie_id,
        media_type
    ))

    conn.commit()
    conn.close()


# -----------------------------
# Get user's watchlist
# -----------------------------

def get_watchlist(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            movie_id,
            media_type,
            title,
            poster_path,
            overview,
            release_date,
            watched
        FROM watchlist
        WHERE user_id = ?
    """, (user_id,))

    movies = cursor.fetchall()

    conn.close()

    return movies


# -----------------------------
# Mark movie as watched
# -----------------------------

def mark_watched(user_id, movie_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE watchlist
        SET watched = 1
        WHERE user_id = ?
        AND movie_id = ?
    """, (
        user_id,
        movie_id
    ))

    conn.commit()
    conn.close()


# -----------------------------
# Check if movie is in watchlist
# -----------------------------

def is_in_watchlist(user_id, movie_id, media_type="movie"):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM watchlist
        WHERE user_id = ?
        AND movie_id = ?
        AND media_type = ?
    """, (
        user_id,
        movie_id,
        media_type
    ))

    result = cursor.fetchone()

    conn.close()

    return result is not None