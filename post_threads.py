import requests
import time
import os
import random
import base64
from datetime import datetime, timezone, timedelta

from config import (
    THREADS_USER_ID_1, THREADS_ACCESS_TOKEN_1,
    THREADS_USER_ID_2, THREADS_ACCESS_TOKEN_2,
    IMGBB_API_KEY, IMAGE_PATH
)

BASE_URL = "https://graph.threads.net/v1.0"
WIB = timezone(timedelta(hours=7))


# ─── DAFTAR CAPTION RANDOM ───────────────────────────────────
CAPTION_LIST = [
    "Update terbaru hari ini! Jangan sampai ketinggalan 🔔",
    "Cek info lengkapnya di sini ya 👀",
    "Sudah update? Yuk simak yang terbaru 📌",
    "Info penting buat kamu, baca sampai habis ya 📋",
    "Jangan lupa share ke teman-teman juga 🔁",
    "Pantau terus update dari kami setiap saat 📊",
    "Yuk simpan post ini biar gak lupa 📍",
    "Update spesial buat kamu hari ini 🌟",
    "Selalu ada yang baru, stay tuned ya 👍",
    "Cek selengkapnya dan kasih tanggapan kamu 💬",
]


def build_caption() -> str:
    """Pilih 1 caption secara random dari daftar"""
    return random.choice(CAPTION_LIST)


def upload_to_imgbb(image_path: str) -> str | None:
    """Upload gambar ke ImgBB, dapat URL publik"""
    try:
        with open(image_path, "rb") as f:
            img_data = f.read()

        encoded = base64.b64encode(img_data).decode("utf-8")

        res = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": IMGBB_API_KEY,
                "image": encoded,
                "expiration": 600  # dihapus otomatis dari imgbb setelah 10 menit
            },
            timeout=30
        )

        if res.status_code != 200:
            print(f"[upload] ERROR upload ImgBB: {res.text}")
            return None

        image_url = res.json()["data"]["url"]
        print(f"[upload] Gambar tersedia di: {image_url}")
        return image_url

    except Exception as e:
        print(f"[upload] ERROR: {e}")
        return None


def create_media_container(user_id: str, access_token: str, image_url: str, caption: str) -> str | None:
    """Step 1: Buat media container di Threads"""
    url = f"{BASE_URL}/{user_id}/threads"
    params = {
        "media_type"   : "IMAGE",
        "image_url"    : image_url,
        "text"         : caption,
        "access_token" : access_token
    }

    res = requests.post(url, params=params, timeout=15)
    if res.status_code != 200:
        print(f"[post] ERROR buat container: {res.text}")
        return None

    container_id = res.json().get("id")
    print(f"[post] Container ID: {container_id}")
    return container_id


def publish_container(user_id: str, access_token: str, container_id: str) -> bool:
    """Step 2: Publish container ke Threads"""
    print("[post] Menunggu 30 detik sebelum publish...")
    time.sleep(30)

    url = f"{BASE_URL}/{user_id}/threads_publish"
    params = {
        "creation_id"  : container_id,
        "access_token" : access_token
    }

    res = requests.post(url, params=params, timeout=15)
    if res.status_code != 200:
        print(f"[post] ERROR publish: {res.text}")
        return False

    post_id = res.json().get("id")
    print(f"[post] ✅ Berhasil diposting! Post ID: {post_id}")
    return True


def post_to_account(user_id: str, access_token: str, image_url: str, caption: str, account_label: str) -> bool:
    """Post lengkap ke satu akun Threads"""
    print(f"\n[post] ── Posting ke {account_label} ──────────")

    if not user_id or not access_token:
        print(f"[post] ⚠️  {account_label}: USER_ID atau ACCESS_TOKEN belum diset")
        return False

    container_id = create_media_container(user_id, access_token, image_url, caption)
    if not container_id:
        return False

    return publish_container(user_id, access_token, container_id)


def post_to_threads() -> dict:
    """
    Fungsi utama:
    1. Upload gambar dari template/ ke ImgBB
    2. Bangun caption random
    3. Post ke Akun 1 dan Akun 2
    """

    result = {"akun_1": False, "akun_2": False}

    if not os.path.exists(IMAGE_PATH):
        print(f"[post] ❌ Gambar tidak ditemukan: {IMAGE_PATH}")
        return result

    image_url = upload_to_imgbb(IMAGE_PATH)
    if not image_url:
        print("[post] ❌ Gagal upload gambar ke ImgBB, batal posting.")
        return result

    caption = build_caption()
    print(f"[post] Caption terpilih: {caption}")

    # ── Post ke Akun 1 ──────────────────────────────────────
    result["akun_1"] = post_to_account(
        THREADS_USER_ID_1, THREADS_ACCESS_TOKEN_1,
        image_url, caption, "AKUN 1"
    )

    # ── Post ke Akun 2 ──────────────────────────────────────
    result["akun_2"] = post_to_account(
        THREADS_USER_ID_2, THREADS_ACCESS_TOKEN_2,
        image_url, caption, "AKUN 2"
    )

    return result


# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    waktu = datetime.now(WIB).strftime("%d %b %Y %H:%M WIB")
    print(f"\n{'='*50}")
    print(f"  POST GAMBAR STATIS — {waktu}")
    print(f"{'='*50}")

    hasil = post_to_threads()

    print(f"\n{'='*50}")
    print(f"  RINGKASAN")
    print(f"  Akun 1 : {'✅ Berhasil' if hasil['akun_1'] else '❌ Gagal'}")
    print(f"  Akun 2 : {'✅ Berhasil' if hasil['akun_2'] else '❌ Gagal'}")
    print(f"{'='*50}\n")
