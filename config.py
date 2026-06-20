import os
from dotenv import load_dotenv

load_dotenv()

# ─── THREADS AKUN 1 ────────────────────────────────────────
THREADS_USER_ID_1      = os.getenv("THREADS_USER_ID_1", "")
THREADS_ACCESS_TOKEN_1 = os.getenv("THREADS_ACCESS_TOKEN_1", "")

# ─── THREADS AKUN 2 ────────────────────────────────────────
THREADS_USER_ID_2      = os.getenv("THREADS_USER_ID_2", "")
THREADS_ACCESS_TOKEN_2 = os.getenv("THREADS_ACCESS_TOKEN_2", "")

# ─── IMGBB (upload gambar ke URL publik) ──────────────────
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")

# ─── PATH GAMBAR ───────────────────────────────────────────
TEMPLATE_FOLDER  = "template"
TOTAL_GAMBAR     = 5
COUNTER_FILE     = "counter.txt"   # simpan indeks gambar terakhir yang dipakai

def get_image_path(index: int) -> str:
    """Path gambar berdasarkan index (1-5)"""
    return f"{TEMPLATE_FOLDER}/post_{index}.png"
