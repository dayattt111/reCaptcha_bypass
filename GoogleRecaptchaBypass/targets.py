from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver
import time
import random

# === DATA LOGIN ===
# User Aril
# 085285887793
# baduut15

# User Nada
# 085894106932
# baduut15

# User Azzhurchuf
# 089653556313
# baduut15

# User Jajang
# 087794222424
# baduut15
USERS = [
    {"phone": "085285887793", "password": "baduut15"},
    {"phone": "085894106932", "password": "baduut15"},
    {"phone": "089653556313", "password": "baduut15"},
    {"phone": "087794222424", "password": "baduut15"},
]

# Pilih user pertama (Anda bisa pilih acak)
USER = USERS[0]

# === CONFIG BROWSER ===
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
for arg in CHROME_ARGUMENTS:
    options.set_argument(arg)

options.set_user_agent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

driver = ChromiumPage(addr_or_opts=options)
solver = RecaptchaSolver(driver)

# === 1. BUKA HALAMAN LOGIN ===
print("➡️ Membuka halaman login...")
driver.get("https://antrean.logammulia.com/login")

# === 2. LOGIN ===
print(f"🔑 Login sebagai: {USER['phone']}")
driver("#phone").input(USER["phone"])
driver("#password").input(USER["password"])

# Selesaikan CAPTCHA login
print("🧩 Menyelesaikan CAPTCHA login...")
try:
    solver.solveCaptcha()
except Exception as e:
    print(f"❌ Gagal CAPTCHA login: {e}")
    input("Tekan Enter untuk keluar...")
    driver.quit()
    exit()

# Submit login
driver.ele("button:contains('Login')").click()
time.sleep(2)

# Cek apakah login sukses
if "logout" not in driver.html.lower():
    print("❌ Login gagal. Periksa data atau CAPTCHA.")
    input("Tekan Enter untuk keluar...")
    driver.quit()
    exit()
print("✅ Login berhasil!")

# === 3. KLIK MENU ANTREAN ===
print("🖱️ Menuju halaman antrean...")
driver.get("https://antrean.logammulia.com/antrian")
time.sleep(2)

# === 4. LOOP CABANG SAMPAI KUOTA TERSEDIA ===
BELM_OPTIONS = [
    ("4", "Balikpapan"),
    ("1", "Bandung"),
    ("19", "Bekasi"),
    ("16", "Bintaro"),
    ("17", "Bogor"),
    ("5", "Denpasar"),
    ("20", "Djuanda"),
    ("6", "Gedung Antam"),
    ("3", "Graha Dipta"),
    ("11", "Makassar"),
    ("10", "Medan"),
    ("12", "Palembang"),
    ("24", "Pekanbaru"),
    ("21", "Puri Indah"),
    ("15", "Semarang"),
    ("23", "Serpong"),
    ("8", "Setiabudi One"),
    ("13", "Surabaya 1 Darmo"),
    ("14", "Surabaya 2 Pakuwon"),
    ("9", "Yogyakarta"),
]

selected_cabang = None
for value, name in BELM_OPTIONS:
    try:
        print(f"\n🔄 Mencoba cabang: {name} (ID: {value})")
        
        # Pilih cabang
        driver.wait.ele_displayed("#site", timeout=10)
        driver("#site").select.by_value(value)
        time.sleep(0.5)

        # Klik "Tampilkan Butik"
        driver.ele("button:contains('Tampilkan Butik')").click()
        time.sleep(2)

        # Cek apakah ada slot tersedia (misal: teks "Tersedia X/5" atau tombol "Ambil Antrean")
        try:
            # Cari elemen waktu dengan teks "Tersedia" dan angka > 0
            wakda_options = driver.eles("option:contains('Tersedia')")
            available = False
            target_value = None
            for opt in wakda_options:
                text = opt.text
                if "Tersedia" in text:
                    # Ekstrak "0/5" → cek apakah bukan "0/5"
                    if "0/5" not in text and "Tersedia 0" not in text:
                        target_value = opt.attrs.get("value")
                        available = True
                        break

            if available and target_value:
                print(f"✅ Kuota tersedia di {name}! Memilih waktu: {text.strip()}")
                selected_cabang = (value, name, target_value)
                break
            else:
                print(f"❌ Tidak ada kuota di {name}")
        except Exception as e:
            print(f"⚠️ Tidak bisa cek kuota di {name}: {e}")

    except Exception as e:
        print(f"⚠️ Error saat coba {name}: {e}")
        continue

if not selected_cabang:
    print("❌ Semua cabang penuh. Tidak ada kuota tersedia.")
    input("Tekan Enter untuk keluar...")
    driver.quit()
    exit()

# === 5. ISI WAKTU & CAPTCHA ANTREAN ===
print("\n⏳ Mengisi waktu kedatangan...")
driver.wait.ele_displayed("#wakda", timeout=10)
driver("#wakda").select.by_value(selected_cabang[2])
time.sleep(0.5)

print("🧩 Menyelesaikan CAPTCHA ambil antrean...")
try:
    solver.solveCaptcha()
except Exception as e:
    print(f"❌ Gagal CAPTCHA ambil antrean: {e}")
    input("Tekan Enter untuk keluar...")
    driver.quit()
    exit()

# Tunggu token
print("⏳ Menunggu token CAPTCHA...")
for _ in range(30):
    if driver("#g-recaptcha-response").value.strip():
        break
    time.sleep(0.3)
else:
    print("⚠️ Token CAPTCHA tidak muncul, tetap lanjut...")

# === 6. KLIK AMBIL ANTREAN ===
print("📤 Mengklik 'Ambil Antrean'...")
driver.ele("button:contains('Ambil Antrean')").click()
time.sleep(2)

# === 7. DETEKSI HASIL ===
if "Berhasil" in driver.html or "success" in driver.html.lower() or "nomor antrean" in driver.html.lower():
    print("🎉 Sukses ambil antrean!")
else:
    print("❓ Form dikirim, tetapi status tidak jelas.")

# === TAHAN BROWSER ===
input("\n👉 Tekan Enter untuk menutup browser...")
driver.quit()