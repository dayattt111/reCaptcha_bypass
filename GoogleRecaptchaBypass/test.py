from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver
import time

CHROME_ARGUMENTS = [
    "-no-first-run",
    "-force-color-profile=srgb",
    "-metrics-recording-only",
    "-password-store=basic",
    "-use-mock-keychain",
    "-export-tagged-pdf",
    "-no-default-browser-check",
    "-disable-background-mode",
    "-enable-features=NetworkService,NetworkServiceInProcess",
    "-disable-features=FlashDeprecationWarning",
    "-deny-permission-prompts",
    "-disable-gpu",
    "-accept-lang=en-US",
    "--disable-usage-stats",
    "--disable-crash-reporter",
    "--no-sandbox",
    "--disable-blink-features=AutomationControlled"
]

options = ChromiumOptions()
for argument in CHROME_ARGUMENTS:
    options.set_argument(argument)

options.set_user_agent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

driver = ChromiumPage(addr_or_opts=options)
recaptchaSolver = RecaptchaSolver(driver)

# === Pilih target ===
# Ganti URL di sini untuk ganti target
TARGET_URL = "https://www.google.com/recaptcha/api2/demo"  # ✅ Ganti ke Logam Mulia jika perlu
# TARGET_URL = "https://antrean.logammulia.com/antrian"

print(f"➡️ Membuka: {TARGET_URL}")
driver.get(TARGET_URL)

# === Deteksi jenis halaman ===
is_logam_mulia = "antrean.logammulia.com" in driver.url
is_google_demo = "google.com/recaptcha/api2/demo" in driver.url

try:
    if is_logam_mulia:
        print("📍 Mode: Logam Mulia Antrean")
        # Tunggu form muncul
        driver.wait.ele_displayed("#site", timeout=15)
        driver("#site").select.by_value("11")  # Makassar
        driver.wait.ele_loaded("#t", timeout=5)
        time.sleep(0.5)
        driver.ele("button:contains('Tampilkan Butik')").click()
        time.sleep(2)

        # Pilih waktu
        driver.wait.ele_displayed("#wakda", timeout=10)
        driver("#wakda").select.by_value("69")
        time.sleep(0.3)

    elif is_google_demo:
        print("🧪 Mode: Google reCAPTCHA Demo")
        # Tidak perlu isi form — langsung CAPTCHA
        pass

    else:
        raise Exception("URL tidak dikenali. Tidak ada logika untuk halaman ini.")

    # === Selesaikan CAPTCHA ===
    print("🧩 Menyelesaikan CAPTCHA...")
    t0 = time.time()
    recaptchaSolver.solveCaptcha()
    print(f"✅ CAPTCHA berhasil dalam {time.time() - t0:.2f} detik.")

    # Tunggu token muncul (aman untuk kedua jenis halaman)
    print("⏳ Menunggu token reCAPTCHA...")
    for _ in range(30):
        resp = driver("#g-recaptcha-response").value
        if resp.strip():
            print("🔑 Token diterima.")
            break
        time.sleep(0.3)
    else:
        print("⚠️ Token tidak muncul, tapi lanjut submit...")

    # === Submit sesuai halaman ===
    if is_logam_mulia:
        print("📤 Submit: Ambil Antrean")
        driver.ele("button:contains('Ambil Antrean')").click()
    elif is_google_demo:
        print("📤 Submit: Demo Form")
        driver.ele("#recaptcha-demo-submit").click()

    print("✅ Formulir dikirim!")

except Exception as e:
    print(f"❌ Error: {e}")

# Tahan browser
input("\n👉 Tekan Enter untuk menutup browser...")
driver.close()

# Jeda waktu sblm broeser ditutup
# time.sleep(10)
# nutup browser
# driver.close()