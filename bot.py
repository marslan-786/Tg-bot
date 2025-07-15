import os
import json
import pytesseract
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes, CallbackQueryHandler,
    MessageHandler, filters
)

BOT_TOKEN = os.environ.get("7973809732:AAH12oB5CLE0sNl_GZ_mnc1K91tv_V_1ZAY")  # OR hardcode here
OWNER_ID = int(os.environ.get("8003357608"))  # Replace with your Telegram chat ID

LINK_FILE = "links.json"

def load_links():
    if os.path.exists(LINK_FILE):
        with open(LINK_FILE, "r") as f:
            return json.load(f)
    return []

def save_links(links):
    with open(LINK_FILE, "w") as f:
        json.dump(links, f)

# OTP logic
def extract_otp_from_image(img_path, keyword):
    text = pytesseract.image_to_string(Image.open(img_path))
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if keyword in line:
            return lines[i + 1] if i + 1 < len(lines) else None
    return None

def fetch_otp(url):
    keyword = "🚨 Join our Telegram channel"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(2)

    driver.save_screenshot("screenshot.png")
    driver.quit()

    otp = extract_otp_from_image("screenshot.png", keyword)
    return otp

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    await update.message.reply_text("✅ VIP OTP Bot connected!\nUse /add to add OTP links.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    await update.message.reply_text("📥 Send me the OTP link to add:")

    context.user_data["awaiting_link"] = True

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_link"):
        url = update.message.text.strip()
        links = load_links()
        links.append(url)
        save_links(links)
        context.user_data["awaiting_link"] = False
        await update.message.reply_text("✅ Link added successfully!", reply_markup=link_markup())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("otp_"):
        link = query.data[4:]
        await query.edit_message_text(f"⏳ Fetching OTP from:\n{link}")
        otp = fetch_otp(link)
        if otp:
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"🔐 OTP from {link}:\n`{otp}`", parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="❌ OTP not found.")

def link_markup():
    links = load_links()
    keyboard = [[InlineKeyboardButton(f"🔗 {i+1}", callback_data=f"otp_{link}")] for i, link in enumerate(links)]
    return InlineKeyboardMarkup(keyboard)

# Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 Bot is running...")
    app.run_polling()
