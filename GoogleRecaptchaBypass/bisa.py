from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver
import time
import random

URL = "https://antrean.logammulia.com/login"

USER = {
    "username": "089603335576",
    "password": "Golddrive123"
}


def find_recaptcha_iframe(page):
    """Cari iframe reCAPTCHA dengan polling."""
    print("🔍 Mencari iframe reCAPTCHA...")
    for _ in range(30):
        iframes = page.eles("tag:iframe")
        for f in iframes:
            src = f.attrs.get("src", "")
            if "google.com/recaptcha" in src:
                print("✅ Iframe reCAPTCHA ditemukan.")
                return f
        time.sleep(0.3)
    return None


def wait_for_captcha_token(page, timeout=15):
    """Tunggu sampai #g-recaptcha-response berisi token."""
    print("⏳ Menunggu token CAPTCHA...")
    for _ in range(timeout * 2):
        try:
            resp = page("#g-recaptcha-response", timeout=1).value
            if resp.strip():
                print("🔑 Token CAPTCHA diterima.")
                return True
        except:
            pass
        time.sleep(0.5)
    print("⚠️ Token CAPTCHA tidak muncul dalam waktu yang ditentukan.")
    return False


def main():
    opts = ChromiumOptions()
    opts.set_argument("--disable-blink-features=AutomationControlled")
    opts.set_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    page = ChromiumPage(opts)
    print("➡️ Membuka halaman login...")
    page.get(URL)

    # Isi username & password
    print("🔑 Mengisi username...")
    page.ele('#username', timeout=10).input(USER["username"])
    time.sleep(random.uniform(0.3, 0.7))

    print("🔒 Mengisi password...")
    page.ele('#password').input(USER["password"])
    time.sleep(random.uniform(0.3, 0.7))

    # Cari dan klik CAPTCHA
    iframe = find_recaptcha_iframe(page)
    if not iframe:
        print("❌ CAPTCHA tidak ditemukan.")
        page.quit()
        return

    print("🖱 Mengklik checkbox CAPTCHA...")
    try:
        iframe.ele(".rc-anchor-content", timeout=5).click()
    except:
        print("❌ Gagal mengklik checkbox CAPTCHA.")
        page.quit()
        return

    time.sleep(1)

    # Selesaikan CAPTCHA
    print("🧩 Menyelesaikan CAPTCHA dengan solver...")
    solver = RecaptchaSolver(page)
    try:
        solver.solveCaptcha()
    except Exception as e:
        print(f"❌ Gagal menyelesaikan CAPTCHA: {e}")
        page.quit()
        return

    # Verifikasi token benar-benar ada
    if not wait_for_captcha_token(page):
        print("⚠️ Lanjut meski token tidak terdeteksi...")

    # Klik tombol login (dengan locator yang tepat)
    print("➡️ Mengklik tombol 'Log in'...")
    try:
        # Gunakan kombinasi: button + type=submit + teks
        # login_btn = page.ele("text=Log in", timeout=10)
        # login_btn = page.ele("button:contains('Log in')", timeout=10)
        login_btn = page.ele("button[type='submit']", timeout=10)
        if not login_btn.states.is_enabled:
            print("⚠️ Tombol login tidak aktif.")
        else:
            time.sleep(random.uniform(1.2, 1.5))  # delay manusiawi
            login_btn.click()
    except Exception as e:
        print(f"❌ Gagal mengklik tombol login: {e}")
        page.quit()
        return

    # Tunggu hasil login
    print("⏳ Menunggu proses login selesai...")
    time.sleep(5)

    # Cek keberhasilan login
    if "antrian" in page.url or page.ele("text=Antrean Butik Emas LM", timeout=3):
        print("🎉 LOGIN BERHASIL! Berada di halaman antrean.")
    else:
        print("❌ Login gagal — cek ulang data atau CAPTCHA.")

    # Opsional: tahan browser
    input("\n👉 Tekan Enter untuk menutup browser...")
    page.quit()


if __name__ == "__main__":
    main()