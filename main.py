import os
import logging
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not all([API_ID, API_HASH, BOT_TOKEN, ADMIN_ID]):
    logging.error("❌ Pastikan semua variabel diatur dalam GitHub Secrets atau file .env.")
    exit()

try:
    ADMIN_ID = int(ADMIN_ID.strip())
except (ValueError, TypeError):
    logging.error("❌ ADMIN_ID tidak valid. Pastikan itu adalah angka.")
    exit()

# Inisialisasi klien bot Pyrogram dan memuat plugin
app = Client(
    "fsub_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    logging.info("🚀 Bot sedang berjalan...")
    app.run()
