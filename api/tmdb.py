import requests

# ─── TMDB ─────────────────────────────────────────────────────────────────────
TMDB_TOKEN = (
    "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2ZDk4ODNlNmViZjVhM2IzZDczMWY5Yj"
    "gzZTMyYWJiMCIsIm5iZiI6MTc3ODg3NjU2Mi4wMzMsInN1YiI6IjZhMDc4MDkyZTIyZTZj"
    "MTUzZjVhNzRjMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.oTH5Qss"
    "S5WrD8ShZG_9CuBrh4nZgdsOtYgtnwSWDNt4"
)
TMDB_BASE    = "https://api.themoviedb.org/3"
IMG_BASE_W   = "https://image.tmdb.org/t/p/w500"
IMG_BASE_O   = "https://image.tmdb.org/t/p/original"
HEADERS      = {"Authorization": TMDB_TOKEN, "accept": "application/json"}
WATCHED_FILE = "watched.json"
def tmdb_get(path, params=None):
    try:
        r = requests.get(f"{TMDB_BASE}{path}", headers=HEADERS, params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None
