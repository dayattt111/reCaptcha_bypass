from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver
import time

URL = "https://antrean.logammulia.com/login"  

USER = {
    "username": "089603335576",
    "password": "Golddrive123"
}

def find_recaptcha_iframe(page):
    """
    Mencari iframe reCAPTCHA di halaman Logam Mulia.
    reCAPTCHA muncul secara dinamis → perlu polling.
    """
    print("🔍 Mencari iframe reCAPTCHA...")

    for _ in range(30):  # coba 30x
        iframes = page.eles("tag:iframe")

        for f in iframes:
            src = f.attrs.get("src", "")
            if "google.com/recaptcha" in src:
                print(f"✅ Iframe ditemukan: {src}")
                return f

        time.sleep(0.3)

    return None


def main():
    opts = ChromiumOptions()
    opts.set_argument("--disable-blink-features=AutomationControlled")

    page = ChromiumPage(opts)

    print("➡️ Membuka halaman login...")
    page.get(URL)

    # === Isi Username ===
    print("🔑 Mengisi username...")
    page.ele('#username', timeout=10).input(USER["username"])

    # === Isi Password ===
    print("🔒 Mengisi password...")
    page.ele('#password').input(USER["password"])

    # === Cari iframe reCAPTCHA ===
    print("☑️ Menunggu iframe reCAPTCHA...")
    iframe = find_recaptcha_iframe(page)

    if not iframe:
        print("❌ reCAPTCHA tidak ditemukan sama sekali!")
        return

    # === Klik Checkbox ===
    print("🖱 Mengklik checkbox reCAPTCHA...")
    try:
        iframe.ele(".recaptcha-checkbox-border", timeout=5).click()
    except:
        print("⚠️ Checkbox tidak bisa diklik langsung. Coba klik anchor...")
        try:
            iframe.ele(".rc-anchor-content", timeout=5).click()
        except:
            print("❌ Gagal klik checkbox.")
            return

    time.sleep(1)

    # === Solve Audio reCAPTCHA ===
    print("🎧 Memulai solver audio...")
    solver = RecaptchaSolver(page)

    try:
        solver.solveCaptcha()
    except Exception as e:
        print(f"❌ Gagal menyelesaikan captcha: {e}")
        return

    print("✅ reCAPTCHA terisi token!")

    # === Klik tombol Login ===
    print("➡️ Klik tombol login...")
    page.ele('button.btn.btn-primary', index=1).click()

    print("⏳ Menunggu proses login...")
    time.sleep(3)

    if "dashboard" in page.url or "home" in page.url:
        print("🎉 LOGIN BERHASIL!")
    else:
        print("⚠️ Login mungkin gagal. Periksa username/password/kapcah.")


if __name__ == "__main__":
    main()
