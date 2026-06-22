import requests
import time
import os
import random
import base64
from datetime import datetime, timezone, timedelta

from config import (
    THREADS_USER_ID_1, THREADS_ACCESS_TOKEN_1,
    THREADS_USER_ID_2, THREADS_ACCESS_TOKEN_2,
    IMGBB_API_KEY, TOTAL_GAMBAR, COUNTER_FILE, get_image_path
)

BASE_URL = "https://graph.threads.net/v1.0"
WIB = timezone(timedelta(hours=7))


# ─── DAFTAR CAPTION RANDOM ───────────────────────────────────
CAPTION_LIST = [
    "BrankasEmas(dot)com kamu bisa tracking nilai aset kamu, sesuai harga terkini harga dasar emas",
    "Gabung dengan BrankasEmas(dot)com , kamu bisa melihat riwayat harga emas dari berbagai brand",
    "BrankasEmas(dot)com membantu kamu tracking nilai aset emas secara real-time berdasarkan harga dasar emas terkini dari berbagai brand",
    "Pantau pergerakan harga dasar emas dari berbagai brand favoritmu di BrankasEmas(dot)com dengan data yang selalu diperbarui.",
    "Simpan, pantau, dan kelola aset emasmu lebih mudah melalui BrankasEmas(dot)com, lengkap dengan riwayat harga emas",
    "Ingin tahu nilai aset emasmu hari ini? BrankasEmas(dot)com menyediakan fitur tracking aset dan harga emas terbaru.",
    "Di BrankasEmas(dot)com, kamu bisa memantau harga emas berbagai brand sekaligus membeli emas dengan lebih praktis",
    "BrankasEmas(dot)com adalah solusi untuk tracking aset emas, melihat riwayat harga, memantau harga dasar emas berbagai brand, dan membeli emas dalam satu platform",
]

# ─── DAFTAR AJAKAN JOIN GRUP (RANDOM) ───────────────────────
PROMOSI_LIST = [
    "Gabung juga dengan grup kami, link di bio",
    "Pantu juga harga emas melalui grup whatsapp, join link ada di bio",
    "Jangan lewatkan update harga emas, link di bio 📊", 
    "Update harga emas. Yuk gabung komunitas kami, link ada di bio 🔗",
    "Grup WA pantau harga emas, join via link yang ada di bio ya",
]

# ─── DAFTAR HASHTAG (RANDOM) ─────────────────────────────────
HASHTAG_LIST = [
    "#finansial",
    "#accounting",
    "#IHSG",
    "#JualLMAntam",
    "#emas hari ini",
    "#antam",
    "#buybackemas",
    "#investasiemas",
    "#beliemas",
    "#Nyabarantam",
    "#LogamMulia",
    "#jewelrythreads",
    "#investing",
    "#jakarta",
    "#emasdigital",
    "#semarnusantara",
    "#terimajualbelimas",
    "#UMKMthreads",
    "#Worklife",
    "#viralThreads",
    "#Ekonomi",
    "#Butikantambekasi",
    "#nabung",
    "#jakartatoday",
    "#emasperhiasan",
    "#galeri24",
    "#emashartadinata",
    "#InvestasiPemula",
    "#perhiasanemas",
    "#EmaskuHartadinata",
]


def get_next_image_index() -> int:
    """
    Baca counter.txt untuk tahu gambar mana yang sudah dipakai terakhir,
    lalu kembalikan index gambar SELANJUTNYA (rotasi 1→2→3→4→5→1...).
    """
    try:
        with open(COUNTER_FILE, "r") as f:
            last_index = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        last_index = 0  # belum pernah jalan, mulai dari awal

    next_index = (last_index % TOTAL_GAMBAR) + 1

    # Simpan index yang dipakai sekarang, untuk run berikutnya
    with open(COUNTER_FILE, "w") as f:
        f.write(str(next_index))

    print(f"[rotasi] Gambar terpilih: post_{next_index}.png")
    return next_index


def build_caption() -> str:
    """Gabungkan caption random + ajakan join grup random + hashtag random + timestamp"""
    waktu   = datetime.now(WIB).strftime("%d-%m-%Y %H:%M WIB")
    caption = random.choice(CAPTION_LIST)
    promosi = random.choice(PROMOSI_LIST)
    hashtag = random.choice(HASHTAG_LIST)

    return f"{caption}\n\n{promosi}\n\n{hashtag}\n\n🕐 {waktu}"
    


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
    1. Tentukan gambar selanjutnya (rotasi 1-5)
    2. Upload gambar dari template/ ke ImgBB
    3. Bangun caption RANDOM TERPISAH untuk masing-masing akun
    4. Post ke Akun 1 dan Akun 2
    """

    result = {"akun_1": False, "akun_2": False}

    index = get_next_image_index()
    image_path = get_image_path(index)

    if not os.path.exists(image_path):
        print(f"[post] ❌ Gambar tidak ditemukan: {image_path}")
        return result

    image_url = upload_to_imgbb(image_path)
    if not image_url:
        print("[post] ❌ Gagal upload gambar ke ImgBB, batal posting.")
        return result

    # Caption dibuat TERPISAH untuk masing-masing akun (independen, tidak sama)
    caption_1 = build_caption()
    caption_2 = build_caption()
    print(f"[post] Caption Akun 1: {caption_1}")
    print(f"[post] Caption Akun 2: {caption_2}")

    # ── Post ke Akun 1 ──────────────────────────────────────
    result["akun_1"] = post_to_account(
        THREADS_USER_ID_1, THREADS_ACCESS_TOKEN_1,
        image_url, caption_1, "AKUN 1"
    )

    # ── Post ke Akun 2 ──────────────────────────────────────
    result["akun_2"] = post_to_account(
        THREADS_USER_ID_2, THREADS_ACCESS_TOKEN_2,
        image_url, caption_2, "AKUN 2"
    )

    return result


# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    sleep_sec = random.randint(65, 200)
    print(f"[main] Menunggu {sleep_sec} detik sebelum posting (biar natural)...")
    time.sleep(sleep_sec)

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
