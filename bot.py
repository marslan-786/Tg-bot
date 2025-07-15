from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import pytesseract
import time
import telegram

# Config
URL = "https://temp-number.com/temporary-numbers/United-Kingdom/447846823127/1"  # ← Replace with your OTP site
KEYWORD = "🚨 Join our Telegram channel @tempnumbers_com to get instant updates whenever new phone numbers are added! 🚨"     # ← Text above the OTP
BOT_TOKEN = "7973809732:AAH12oB5CLE0sNl_GZ_mnc1K91tv_V_1ZAY"
CHAT_ID = "8003357608"

# Headless browser setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,720")

# Optional: Disable images, JS, and ads (basic level)
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.javascript": 1  # if OTP uses JS, keep this 1
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)

# Telegram bot init
bot = telegram.Bot(token=BOT_TOKEN)

def extract_otp_from_image(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    lines = text.splitlines()
    otp = None
    for i, line in enumerate(lines):
        if KEYWORD in line:
            otp = lines[i + 1] if i + 1 < len(lines) else None
            break
    return otp

def run_otp_bot():
    last_otp = None
    while True:
        driver.get(URL)
        time.sleep(2)

        # Remove known ad elements using JS
        ad_block_js = """
            const selectors = ['#ad', '#ads', '.ad', '.adsbygoogle', '#bannerAd'];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.remove());
            });
        """
        driver.execute_script(ad_block_js)

        # Screenshot
        driver.save_screenshot("screenshot.png")
        otp = extract_otp_from_image("screenshot.png")

        if otp and otp != last_otp:
            last_otp = otp
            bot.send_message(chat_id=CHAT_ID, text=f"🔐 New OTP:\n`{otp}`", parse_mode="Markdown")

        time.sleep(5)

run_otp_bot()
