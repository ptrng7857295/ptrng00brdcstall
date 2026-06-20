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
TEMPLATE_FOLDER = "template"
IMAGE_FILENAME  = "post_image.png"   # nama file gambar yang kamu upload manual
IMAGE_PATH      = f"{TEMPLATE_FOLDER}/{IMAGE_FILENAME}"
