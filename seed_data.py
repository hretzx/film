"""
Seed script for the CINEBOOK practice project.

Run from the project root (where manage.py lives):

    python seed_data.py

What it does (idempotent — safe to re-run):
  1. Ensures all tables exist (movie, users, showDetails, seats, payment).
  2. Seeds a few dummy movies *only if* the movie table is empty.
  3. Seeds a demo login user (demo / demo123) if it doesn't exist.
  4. RESETS showDetails, seats and payment, then re-seeds the predefined
     shows + seat configuration for EVERY movie.

Step 4 wipes existing bookings/history so the data stays consistent.
"""

import os
import json
import config
import mysql.connector as m

# Local poster images live in /images and are served at /static/ (see settings.py).
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
STATIC_PREFIX = "/static/"

try:
    import bcrypt
except ImportError:  # pragma: no cover
    bcrypt = None

# --- Predefined configuration (mirrors booking/views.py) ----------------------

PREDEFINED_SHOWS = [
    ("Screen 1", "Standard Theatre",  "Today • 10:30 AM",   250),
    ("Screen 1", "Standard Theatre",  "Today • 2:00 PM",    250),
    ("Screen 2", "Digital 4K Cinema", "Today • 5:30 PM",    300),
    ("IMAX",     "IMAX Laser 70mm",   "Tomorrow • 6:45 PM", 500),
]
SEAT_ROWS = ["A", "B", "C", "D", "E"]
SEATS_PER_ROW = 8
PREBOOKED_SEATS = {"A3", "A7", "B2", "B8", "C5", "D1", "D7", "E6"}

# Dummy movies — only inserted when the movie table is empty.
# Columns: title, actors, director, rating, duration, description, crew, genre, languages, poster_url
DUMMY_MOVIES = [
    {
        "title": "Oppenheimer", "director": "Christopher Nolan", "rating": 9, "duration": 180,
        "description": "The story of J. Robert Oppenheimer and the creation of the atomic bomb.",
        "actors": ["Cillian Murphy", "Emily Blunt", "Robert Downey Jr."],
        "crew": ["Hoyte van Hoytema (DoP)", "Ludwig Goransson (Music)"],
        "genre": ["Biography", "Drama"], "languages": ["English"],
        "poster_url": "/static/oppenheimer.webp",
    },
    {
        "title": "The Brutalist", "director": "Brady Corbet", "rating": 8, "duration": 215,
        "description": "A visionary architect flees post-war Europe to rebuild his life in America.",
        "actors": ["Adrien Brody", "Felicity Jones", "Guy Pearce"],
        "crew": ["Lol Crawley (DoP)", "Daniel Blumberg (Music)"],
        "genre": ["Drama", "History"], "languages": ["English"],
        "poster_url": "/static/thebrutalist.webp",
    },
    {
        "title": "Past Lives", "director": "Celine Song", "rating": 8, "duration": 105,
        "description": "Two childhood friends are reunited decades later for one fateful week.",
        "actors": ["Greta Lee", "Teo Yoo", "John Magaro"],
        "crew": ["Shabier Kirchner (DoP)", "Christopher Bear (Music)"],
        "genre": ["Romance", "Drama"], "languages": ["English", "Korean"],
        "poster_url": "/static/pastlives.webp",
    },
    {
        "title": "All of Us Strangers", "director": "Andrew Haigh", "rating": 8, "duration": 105,
        "description": "A screenwriter reconnects with his late parents while falling for a neighbour.",
        "actors": ["Andrew Scott", "Paul Mescal", "Claire Foy"],
        "crew": ["Jamie D. Ramsay (DoP)", "Emilie Levienaise-Farrouch (Music)"],
        "genre": ["Romance", "Fantasy"], "languages": ["English"],
        "poster_url": "/static/allofusstrangers.webp",
    },
    {
        "title": "Dune: Part Two", "director": "Denis Villeneuve", "rating": 9, "duration": 166,
        "description": "Paul Atreides unites with the Fremen to wage war against House Harkonnen.",
        "actors": ["Timothee Chalamet", "Zendaya", "Rebecca Ferguson"],
        "crew": ["Greig Fraser (DoP)", "Hans Zimmer (Music)"],
        "genre": ["Sci-Fi", "Adventure"], "languages": ["English"],
        "poster_url": "/static/dune.webp",
    },
    {
        "title": "Saltburn", "director": "Emerald Fennell", "rating": 7, "duration": 131,
        "description": "A student at Oxford finds himself drawn into the world of a charming aristocrat.",
        "actors": ["Barry Keoghan", "Jacob Elordi", "Rosamund Pike"],
        "crew": ["Linus Sandgren (DoP)", "Anthony Willis (Music)"],
        "genre": ["Thriller", "Drama"], "languages": ["English"],
        "poster_url": "/static/saltburn.webp",
    },
]


def ensure_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS movie(
        id          INT PRIMARY KEY AUTO_INCREMENT,
        title       VARCHAR(100),
        actors      JSON,
        director    VARCHAR(100),
        rating      INT,
        duration    INT,
        description VARCHAR(1000),
        crew        JSON,
        genre       JSON,
        langauges   JSON,
        poster_url  VARCHAR(1000)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        uid      INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(100) UNIQUE,
        email    VARCHAR(150),
        password VARCHAR(255)
    )""")


def reset_booking_tables(cur):
    """Drop and recreate the booking tables so the schema matches booking/views.py.

    Older versions of this DB created showDetails/seats with different columns
    (location/timing, seat_type), which break the app's queries — recreating
    guarantees a consistent, correct schema.
    """
    cur.execute("DROP TABLE IF EXISTS payment")
    cur.execute("DROP TABLE IF EXISTS seats")
    cur.execute("DROP TABLE IF EXISTS showDetails")
    cur.execute("""
    CREATE TABLE showDetails(
        show_id   INT PRIMARY KEY AUTO_INCREMENT,
        movie_id  INT,
        screen    VARCHAR(50),
        format    VARCHAR(50),
        show_time VARCHAR(50)
    )""")
    cur.execute("""
    CREATE TABLE seats(
        seat_id INT PRIMARY KEY AUTO_INCREMENT,
        show_id INT,
        seat_no VARCHAR(10),
        price   INT,
        status  VARCHAR(20) DEFAULT 'available'
    )""")
    cur.execute("""
    CREATE TABLE payment(
        pid            INT PRIMARY KEY AUTO_INCREMENT,
        seat_id        INT,
        cname          VARCHAR(100),
        amt            INT,
        payment_status VARCHAR(20),
        uid            INT
    )""")


def seed_movies(cur):
    cur.execute("select count(*) from movie")
    if cur.fetchone()[0] > 0:
        print("movies: already present, skipping movie seed")
        return
    for mv in DUMMY_MOVIES:
        cur.execute(
            """insert into movie(title,actors,director,rating,duration,description,crew,genre,langauges,poster_url)
               values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                mv["title"], json.dumps(mv["actors"]), mv["director"], mv["rating"],
                mv["duration"], mv["description"], json.dumps(mv["crew"]),
                json.dumps(mv["genre"]), json.dumps(mv["languages"]), mv["poster_url"],
            ),
        )
    print("movies: seeded %d dummy movies" % len(DUMMY_MOVIES))


def _norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def update_movie_posters(cur):
    """Match each movie title to an image file in /images and point poster_url at it."""
    if not os.path.isdir(IMAGE_DIR):
        print("posters: no images/ directory, skipping")
        return
    exts = (".webp", ".jpg", ".jpeg", ".png")
    images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(exts)]
    stems = {os.path.splitext(f)[0]: f for f in images}  # e.g. "oppenheimer" -> "oppenheimer.webp"

    cur.execute("select id,title from movie")
    updated = 0
    for mid, title in cur.fetchall():
        nt = _norm(title)
        match = None
        for stem, fname in stems.items():
            ns = _norm(stem)
            if nt == ns or nt.startswith(ns) or ns.startswith(nt) or ns in nt or nt in ns:
                match = fname
                break
        if match:
            cur.execute("update movie set poster_url=%s where id=%s", (STATIC_PREFIX + match, mid))
            updated += 1
        else:
            print("posters: no image match for '%s'" % title)
    print("posters: updated %d movie posters to local images" % updated)


def seed_demo_user(cur):
    cur.execute("select count(*) from users where username=%s", ("demo",))
    if cur.fetchone()[0] > 0:
        print("user:   'demo' already exists, skipping")
        return
    if bcrypt is None:
        print("user:   bcrypt not installed, skipping demo user")
        return
    hashed = bcrypt.hashpw(b"demo123", bcrypt.gensalt(rounds=12)).decode("utf-8")
    cur.execute(
        "insert into users(username,email,password) values(%s,%s,%s)",
        ("demo", "demo@cinebook.test", hashed),
    )
    print("user:   seeded demo user (username: demo / password: demo123)")


def seed_shows_and_seats(cur):
    cur.execute("select id,title from movie order by id")
    movies = cur.fetchall()
    total_shows = 0
    total_seats = 0
    for movie_id, title in movies:
        for screen, fmt, show_time, price in PREDEFINED_SHOWS:
            cur.execute(
                "insert into showDetails(movie_id,screen,format,show_time) values(%s,%s,%s,%s)",
                (movie_id, screen, fmt, show_time),
            )
            show_id = cur.lastrowid
            total_shows += 1
            for row in SEAT_ROWS:
                for n in range(1, SEATS_PER_ROW + 1):
                    seat_no = "%s%d" % (row, n)
                    status = "booked" if seat_no in PREBOOKED_SEATS else "available"
                    cur.execute(
                        "insert into seats(show_id,seat_no,price,status) values(%s,%s,%s,%s)",
                        (show_id, seat_no, price, status),
                    )
                    total_seats += 1
    print("shows:  seeded %d shows across %d movies" % (total_shows, len(movies)))
    print("seats:  seeded %d seats (%d pre-booked per show)" % (total_seats, len(PREBOOKED_SEATS)))


def main():
    db = m.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD)
    cur = db.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS movies")
    cur.execute("USE movies")

    ensure_tables(cur)
    seed_movies(cur)
    update_movie_posters(cur)
    seed_demo_user(cur)
    reset_booking_tables(cur)
    seed_shows_and_seats(cur)

    db.commit()
    cur.close()
    db.close()
    print("\nDone. Seed complete.")


if __name__ == "__main__":
    main()
