"""
gaskan_antiban.py
Versi: Anti-Ban friendly automation script untuk https://antrean.logammulia.com/login

CATATAN PENTING:
- Skrip ini TIDAK otomatis mem-bypass Google reCAPTCHA.
- Skrip menunggu token #g-recaptcha-response dan akan berlanjut hanya setelah token tersedia.
- Jika kamu memiliki solver pihak ketiga yang legal (2Captcha/AntiCaptcha/Capsolver) dan
  kamu ingin integrasi, sebutkan layanan itu dan konfirmasi bahwa penggunaannya sah;
  aku bisa bantu menambahkan integrasi setelah konfirmasi.
- Isi daftar PROXIES jika mau pakai rotating proxy.
"""

import time
import random
import sys
from typing import List, Optional
from DrissionPage import ChromiumPage, ChromiumOptions

# ---------------------------
# CONFIG
# ---------------------------
URL_LOGIN = "https://antrean.logammulia.com/login"

USER = {
    "username": "085285887793",  
    "password": "Golddrive123"       
}

# Optional: isi proxy list jika ingin rotasi proxy (format: "http://user:pass@host:port" atau "http://host:port")
PROXIES: List[str] = [
    # "http://127.0.0.1:8000",
    # "http://user:pass@proxy.example:3128",
]

# Limit retry bila terkena blok
MAX_RETRY_ON_BLOCK = 5

# Randomization helpers
def human_delay(a=0.2, b=0.6):
    """Random small delay to look human."""
    time.sleep(random.uniform(a, b))

def human_typing(ele, text: str, min_delay=0.05, max_delay=0.18):
    """Ketik karakter per karakter dengan delay acak."""
    for ch in text:
        ele.input(ch)  # gunakan input per-char (DrissionPage mendukung .input())
        time.sleep(random.uniform(min_delay, max_delay))
    human_delay(0.2, 0.5)

def pick_proxy_cycle(proxies: List[str], attempt: int) -> Optional[str]:
    if not proxies:
        return None
    return proxies[attempt % len(proxies)]

# ---------------------------
# Browser / options builder
# ---------------------------
def build_options(proxy: Optional[str] = None) -> ChromiumOptions:
    opts = ChromiumOptions()
    # Basic anti-automation arguments
    opts.set_argument("-no-first-run")
    opts.set_argument("-no-default-browser-check")
    opts.set_argument("--disable-blink-features=AutomationControlled")
    opts.set_argument("--disable-gpu")
    opts.set_argument("--disable-dev-shm-usage")
    opts.set_argument("--disable-extensions")
    opts.set_argument("--lang=id-ID,id")
    opts.set_argument("--window-size=1200,800")
    opts.incognito()  # jika tersedia

    # User agent (jangan gunakan default headless UA)
    opts.set_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    # Proxy jika diberikan
    if proxy:
        # DrissionPage supports set_proxy in options on certain versions; adjust if needed
        try:
            opts.set_proxy(proxy)
        except Exception:
            # fallback: set argument for proxy server (some versions)
            opts.set_argument(f'--proxy-server={proxy}')

    return opts

# ---------------------------
# Util: detect Oops/Block page
# ---------------------------
def is_block_page(page: ChromiumPage) -> bool:
    """Cek apakah halaman menampilkan pesan pemblokiran IP atau 'Oops' page."""
    try:
        html = page.html.lower()
        if "pemblokiran ip sementara" in html or "oops! terjadi kesalahan" in html or "memberlakukan pemblokiran ip sementara" in html:
            return True
        # juga cek teks notifikasi umum
        if "sesi yang terdeteksi melakukan permintaan yang sangat masif" in html:
            return True
    except Exception:
        return False
    return False

# ---------------------------
# Main flow
# ---------------------------
def run_once(proxy: Optional[str] = None):
    opts = build_options(proxy)
    page = ChromiumPage(addr_or_opts=opts)

    try:
        print(f"➡️ Opening {URL_LOGIN}")
        page.get(URL_LOGIN)
        # tunggu network idle / load completed jika tersedia
        try:
            page.wait_for_load_state("networkidle")
        except Exception:
            # fallback
            time.sleep(1.0)

        human_delay(0.5, 1.2)

        # jika halaman menunjukkan blok, return status
        if is_block_page(page):
            print("⚠️ Situs mendeteksi aktivitas tidak wajar / memblokir IP.")
            page.close()
            return False, "blocked"

        # isi username
        print("🔑 Mengisi username...")
        try:
            username_ele = page.ele('#username', timeout=6)
        except Exception:
            print("❌ Tidak menemukan #username pada halaman (mungkin halaman berubah / diblokir).")
            page.close()
            return False, "no-username"

        # human typing: clear first then type char by char
        try:
            username_ele.clear()
        except Exception:
            pass
        human_typing(username_ele, USER["username"], min_delay=0.06, max_delay=0.16)

        human_delay(0.4, 1.0)

        # isi password (lebih aman: ketik manual)
        print("🔒 Mengisi password...")
        try:
            password_ele = page.ele('#password', timeout=6)
        except Exception:
            print("❌ Tidak menemukan #password pada halaman.")
            page.close()
            return False, "no-password"

        try:
            password_ele.clear()
        except Exception:
            pass
        human_typing(password_ele, USER["password"], min_delay=0.06, max_delay=0.16)

        human_delay(0.6, 1.2)

        # Scroll sedikit / gerak mouse untuk meniru pengguna nyata
        try:
            # beberapa method berbeda tersedia; gunakan try/except
            page.run_js("window.scrollBy(0, 120);")
        except Exception:
            pass
        human_delay(0.3, 0.9)

        # small random mouse moves (best-effort)
        try:
            # DrissionPage mungkin punya actions; gunakan jika ada
            if hasattr(page, "actions"):
                try:
                    page.actions.move_by_offset(30, 20).pause(0.25).move_by_offset(-15, 10).perform()
                except Exception:
                    pass
        except Exception:
            pass

        # tunggu captcha muncul; kita tidak akan auto-bypass
        print("🧩 Menunggu reCAPTCHA token (#g-recaptcha-response) — harap selesaikan captcha secara manual jika muncul.")
        token = ""
        for i in range(60):  # tunggu sampai 18 detik (60 * 0.3)
            try:
                token = page("#g-recaptcha-response").value
            except Exception:
                token = ""
            if token and token.strip():
                print("🔑 Token reCAPTCHA terdeteksi.")
                break
            time.sleep(0.3)

        if not token or not token.strip():
            print("⚠️ Token reCAPTCHA tidak ditemukan otomatis. Kamu harus menyelesaikan captcha manual di browser.")
            # beri waktu lebih panjang untuk manual solve
            for i in range(120):  # ~ 36 detik
                try:
                    token = page("#g-recaptcha-response").value
                except Exception:
                    token = ""
                if token and token.strip():
                    print("🔑 Token reCAPTCHA terdeteksi (setelah menunggu).")
                    break
                time.sleep(0.3)

        if not token or not token.strip():
            print("❗Tidak ada token reCAPTCHA setelah menunggu. Akan membatalkan percobaan ini.")
            page.close()
            return False, "no-token"

        human_delay(0.4, 1.0)

        # Klik tombol login (safe selector)
        print("➡️ Mengirimkan form login...")
        try:
            # cari tombol login berdasarkan teks atau kelas
            try:
                btn = page.ele("button.btn.btn-primary", timeout=5)
            except Exception:
                btn = page.ele("button[type='submit']", timeout=5)
            btn.click()
        except Exception as e:
            print("❌ Gagal klik tombol submit:", e)
            page.close()
            return False, "submit-failed"

        # tunggu redirect / response
        human_delay(1.5, 3.0)
        try:
            page.wait_for_load_state("networkidle")
        except Exception:
            time.sleep(2.0)

        # cek apakah berhasil (heuristik sederhana)
        if "dashboard" in page.url or "home" in page.url or "logout" in page.html.lower():
            print("🎉 Login berhasil (heuristik).")
            page.close()
            return True, "ok"

        # cek apakah kembali ke halaman blok
        if is_block_page(page):
            print("⚠️ Setelah submit, situs kembali menampilkan blok.")
            page.close()
            return False, "blocked"

        # jika belum jelas, kita bisa memeriksa presence of error messages
        html = page.html.lower()
        if "invalid" in html or "gagal" in html or "incorrect" in html:
            print("⚠️ Terlihat ada kesalahan login (invalid credentials atau captcha).")
            page.close()
            return False, "login-failed"

        print("ℹ️ Submit telah dikirim tapi hasil tidak jelas. Periksa manual di browser.")
        page.close()
        return False, "unknown"

    except Exception as ex:
        print("❌ Exception:", ex)
        try:
            page.close()
        except Exception:
            pass
        return False, "exception"

# ---------------------------
# Runner dengan retry + proxy rotation + backoff
# ---------------------------
def run_with_retries():
    attempt = 0
    backoff = 5  # detik
    while attempt < MAX_RETRY_ON_BLOCK:
        proxy = pick_proxy_cycle(PROXIES, attempt) if PROXIES else None
        if proxy:
            print(f"🔁 Attempt #{attempt+1} menggunakan proxy: {proxy}")
        else:
            print(f"🔁 Attempt #{attempt+1} tanpa proxy")

        ok, status = run_once(proxy)
        if ok:
            print("✅ Selesai dengan sukses.")
            return True
        else:
            print(f"❗ Percobaan gagal (status={status}). Backoff {backoff}s sebelum retry.")
            time.sleep(backoff + random.uniform(0, 2.0))
            backoff = min(backoff * 2, 120)  # exponential backoff
            attempt += 1

    print("🚫 Sudah mencapai batas retry. Hentikan percobaan.")
    return False

# ---------------------------
# ENTRYPOINT
# ---------------------------
if __name__ == "__main__":
    print("=== Gaskan Anti-Ban Runner ===")
    print("Catatan: script menunggu reCAPTCHA token. Jangan tambahkan auto-solver tanpa izin.")
    success = run_with_retries()
    if success:
        print("Selesai: proses login berhasil atau setidaknya dikirim.")
    else:
        print("Gagal: cek koneksi, IP, atau coba dengan proxy / jeda lebih lama.")
