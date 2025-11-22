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
    "--no-sandbox"
]

options = ChromiumOptions()
for argument in CHROME_ARGUMENTS:
    options.set_argument(argument)

driver = ChromiumPage(addr_or_opts=options)
recaptchaSolver = RecaptchaSolver(driver)

driver.get("https://www.google.com/recaptcha/api2/demo")  # Perbaiki spasi
t0 = time.time()

try:
    recaptchaSolver.solveCaptcha()
    print(f"Time to solve the captcha: {time.time()-t0:.2f} seconds")

    # Tunggu hingga token muncul di form field
    print("Waiting for reCAPTCHA response...")
    for _ in range(30):
        resp = driver("#g-recaptcha-response").value
        if resp.strip():
            print("Token received!")
            break
        time.sleep(0.3)
    else:
        raise Exception("Timeout: reCAPTCHA response not populated")

except Exception as e:
    print(f"Failed to solve the captcha: {str(e)}")
else:
    # Submit form setelah CAPTCHA benar-benar siap
    driver.ele("#recaptcha-demo-submit").click()
    print("Form submitted!")

# Jeda waktu sblm broeser ditutup
time.sleep(10)
# nutup browser
driver.close()