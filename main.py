import os
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ambil konfigurasi dari file .env
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
ADMIN_ID = os.getenv("ADMIN_ID")

if not all([API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, CHANNEL_LINK, ADMIN_ID]):
    logging.error("❌ Pastikan semua variabel diatur dalam file .env.")
    exit()

try:
    ADMIN_ID = int(ADMIN_ID.strip())
    CHANNEL_ID = int(CHANNEL_ID.strip())
except (ValueError, TypeError):
    logging.error("❌ ADMIN_ID atau CHANNEL_ID tidak valid. Pastikan itu adalah angka.")
    exit()

app = Client(
    "fsub_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def get_video_list():
    """Membaca data video dari videos.json"""
    try:
        with open("videos.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_video_list(video_list):
    """Menyimpan data video ke videos.json"""
    with open("videos.json", "w") as f:
        json.dump(video_list, f, indent=4)

async def check_subscription(user_id):
    """Memeriksa keanggotaan dengan cara yang paling andal."""
    logging.info(f"Mengecek langganan pengguna {user_id} di channel {CHANNEL_ID}...")
    try:
        async for member in app.get_chat_members(chat_id=CHANNEL_ID):
            if member.user.id == user_id:
                logging.info(f"Status keanggotaan: ditemukan.")
                return True
        logging.info(f"Status keanggotaan: tidak ditemukan.")
        return False
    except Exception as e:
        logging.error(f"Error saat memeriksa langganan: {e}")
        return False

# --- Handler untuk menambahkan video secara otomatis (khusus admin)
@app.on_message(filters.user(ADMIN_ID) & filters.private & filters.command("addvideo", prefixes="/"))
async def add_video_handler(client, message):
    reply_message = message.reply_to_message
    if not reply_message or not reply_message.video:
        await message.reply_text("❌ Mohon balas video dengan perintah /addvideo <nama_video>.")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ Mohon berikan nama untuk video ini. Contoh: `/addvideo video_utama`")
        return
    
    parameter_name = message.command[1]
    file_id = reply_message.video.file_id
    
    video_list = get_video_list()
    video_list[parameter_name] = file_id
    save_video_list(video_list)
    
    await message.reply_text(
        f"✅ Video dengan nama `{parameter_name}` telah disimpan! "
        f"Bagikan dengan link: `https://t.me/{client.me.username}?start={parameter_name}`"
    )
    logging.info(f"Admin menambahkan video baru: {parameter_name}")

# Handler perintah /start
@app.on_message(filters.command("start", prefixes="/"))
async def start_command(client, message):
    user_id = message.from_user.id
    
    # Ambil parameter dari perintah /start jika ada
    start_parameter = message.command[1] if len(message.command) > 1 else ""

    is_subscribed = await check_subscription(user_id)
    
    if not is_subscribed:
        pesan = f"❌ Anda belum bergabung ke channel kami.\n\nSilakan bergabung ke channel di bawah ini untuk bisa menggunakan bot ini."
        
        # Buat link "Coba Lagi" dengan parameter yang sama
        coba_lagi_link = f"https://t.me/{client.me.username}?start={start_parameter}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Gabung Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("Coba Lagi", url=coba_lagi_link)]
        ])
        await message.reply_text(pesan, reply_markup=keyboard)
    else:
        video_list = get_video_list()
        video_to_send = video_list.get(start_parameter)

        if video_to_send:
            try:
                await message.reply_video(
                    video=video_to_send,
                    caption="✅ Selamat datang! Anda berhasil bergabung ke channel."
                )
            except Exception as e:
                await message.reply_text(f"❌ Terjadi kesalahan saat mengirim video: {e}")
                logging.error(f"Kesalahan pengiriman video: {e}")
        else:
            await message.reply_text(f"✅ Anda sudah bergabung. Namun, parameter video tidak valid.")

if __name__ == "__main__":
    app.run()
