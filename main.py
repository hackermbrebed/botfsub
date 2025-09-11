# Copyright (c) 2025 @hacker.mbrebed
# This script is licensed under the MIT License.
# See the LICENSE file for details.
import os
import json
import logging
import html

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.error import Forbidden

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Memuat variabel dari file .env
from dotenv import load_dotenv
load_dotenv()

# Mengambil token bot dari variabel lingkungan
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Validasi BOT_TOKEN
if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN tidak ditemukan di file .env. Pastikan Anda sudah mengisinya.")
    exit()

# --- Fungsi dan Utilitas Konfigurasi ---
def get_config():
    """Membaca konfigurasi bot dari bot_config.json."""
    try:
        with open("bot_config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Buat konfigurasi default jika file tidak ada
        return {
            "admin_ids": [],
            "fsub_channels": [],
            "fsub_buttons": [],
            "welcome_message": "❌ Anda belum bergabung ke channel kami.\n\nSilakan bergabung ke channel berikut untuk bisa menggunakan bot ini.",
            "photo_id": None,
            "videos": {},
            "user_ids": []
        }

def save_config(config):
    """Menyimpan konfigurasi bot ke bot_config.json. (SUDAH DIPERBAIKI)"""
    with open("bot_config.json", "w") as f:
        json.dump(config, f, indent=4)

async def check_subscription(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Memeriksa apakah pengguna berlangganan ke saluran yang diperlukan."""
    config = get_config()
    channels_to_check = config.get("fsub_channels", [])
    
    unsubscribed_channels = []

    for channel_id in channels_to_check:
        try:
            member: ChatMember = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                unsubscribed_channels.append(channel_id)
        except Exception as e:
            logging.error(f"Error checking subscription for channel {channel_id}: {e}")
            unsubscribed_channels.append(channel_id)

    return len(unsubscribed_channels) == 0, unsubscribed_channels

# --- Handler Perintah Bot (Untuk Semua Pengguna) ---
async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /setup untuk mengatur admin pertama."""
    config = get_config()
    if config["admin_ids"]:
        await update.message.reply_text("<blockquote>❌ Bot sudah diatur. Perintah ini hanya bisa digunakan sekali.</blockquote>", parse_mode=ParseMode.HTML)
        return

    admin_id = update.effective_user.id
    config["admin_ids"].append(admin_id)
    save_config(config)

    await update.message.reply_text("<blockquote>✅ Pengaturan bot berhasil! Anda adalah admin sekarang.</blockquote>", parse_mode=ParseMode.HTML)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /start."""
    config = get_config()
    if not config["admin_ids"]:
        await update.message.reply_text("<blockquote>❌ Bot belum diatur. Gunakan perintah /setup terlebih dahulu untuk menjadi admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
        
    user_ids = set(config.get("user_ids", []))
    user_ids.add(update.effective_user.id)
    config["user_ids"] = list(user_ids)
    save_config(config)

    user_id = update.effective_user.id
    start_parameter = context.args[0] if context.args else None
    
    is_subscribed, _ = await check_subscription(context, user_id)
    
    if not is_subscribed:
        welcome_message = config.get('welcome_message', '❌ Anda belum bergabung ke channel kami.\n\nSilakan bergabung ke channel berikut untuk bisa menggunakan bot ini.')
        message_text = f"<blockquote>{html.escape(welcome_message)}</blockquote>"
        
        keyboard_buttons = []
        for btn in config.get("fsub_buttons", []):
            keyboard_buttons.append([InlineKeyboardButton(btn.get("text"), url=btn.get("url"))])
        
        coba_lagi_link = f"https://t.me/{context.bot.username}?start={start_parameter or ''}"
        keyboard_buttons.append([InlineKeyboardButton("Coba Lagi", url=coba_lagi_link)])
        
        keyboard = InlineKeyboardMarkup(keyboard_buttons)
        photo_id = config.get("photo_id")
        
        if photo_id:
            await update.message.reply_photo(photo=photo_id, caption=message_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(message_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        video_list = config.get("videos", {})
        
        if not start_parameter:
            await update.message.reply_text("<blockquote>✅ Anda sudah bergabung. Gunakan link yang dikirim admin.</blockquote>", parse_mode=ParseMode.HTML)
            return

        video_to_send = video_list.get(start_parameter)

        if video_to_send:
            try:
                caption_text = "<blockquote>Enjoy aja nontonnya☕.</blockquote>"
                await update.message.reply_video(video=video_to_send, caption=caption_text, parse_mode=ParseMode.HTML)
            except Exception as e:
                await update.message.reply_text(f"<blockquote>❌ Terjadi kesalahan saat mengirim video: {html.escape(str(e))}</blockquote>", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("<blockquote>✅ Anda sudah bergabung. Gunakan link yang dikirim admin.</blockquote>", parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan daftar perintah yang tersedia."""
    config = get_config()
    is_admin = update.effective_user.id in config.get("admin_ids", [])
    
    help_message = "                         🛠️<b>Daftar Perintah Bot:</b>\n\n"
    help_message += "          👤<b>Untuk Semua Pengguna:</b>\n"
    help_message += "🔥 <i>/start</i> - Memulai bot.\n"
    help_message += "🔥 <i>/help</i> - Menampilkan daftar perintah bot.\n\n"
    
    if not is_admin:
      await update.message.reply_text(f"<blockquote>{help_message}</blockquote>", parse_mode=ParseMode.HTML)
      return

    help_message += "          👤<b>Untuk Admin:</b>\n"
    help_message += "🔥 <i>/addfsubchannel &lt;id_channel&gt;</i> - Menambahkan channel.\n"
    help_message += "🔥 <i>/delfsubchannel &lt;id_channel&gt;</i> - Menghapus channel.\n"
    help_message += "🔥 <i>/addfsubbutton &lt;teks&gt; &lt;url&gt;</i> - Menambahkan tombol.\n"
    help_message += "🔥 <i>/delfsubbutton &lt;teks&gt;</i> - Menghapus tombol.\n"
    help_message += "🔥 <i>/listfsub</i> - Menampilkan daftar channel dan tombol.\n"
    help_message += "🔥 <i>/setwelcome</i> - Mengatur pesan sambutan.\n"
    help_message += "🔥 <i>/getprofil</i> - Mengatur gambar sambutan.\n"
    help_message += "🔥 <i>/addvideo &lt;nama_video&gt;</i> - Menambahkan video & membuat link.\n"
    help_message += "🔥 <i>/broadcast</i> - Mengirim pesan broadcast ke semua pengguna.\n"
    help_message += "🔥 <i>/addbutton &lt;teks&gt; &lt;url&gt;</i> - Menambahkan tombol untuk broadcast.\n"
    
    await update.message.reply_text(f"<blockquote>{help_message}</blockquote>", parse_mode=ParseMode.HTML)

# --- Handler Admin (Perintah khusus Admin) ---
async def add_fsub_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menambah channel untuk FSub."""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("<blockquote>❌ Mohon sertakan ID channel. Contoh:\n<code>/addfsubchannel -100123456789</code></blockquote>", parse_mode=ParseMode.HTML)
        return
    
    channel_id_str = context.args[0]
    try:
        channel_id = int(channel_id_str)
        if channel_id in config.get("fsub_channels", []):
            await update.message.reply_text("<blockquote>✅ Channel sudah ada di daftar FSub.</blockquote>", parse_mode=ParseMode.HTML)
            return

        config["fsub_channels"].append(channel_id)
        save_config(config)
        await update.message.reply_text(f"<blockquote>✅ Channel dengan ID {channel_id} berhasil ditambahkan ke daftar FSub.</blockquote>", parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("<blockquote>❌ ID channel tidak valid. Pastikan itu adalah angka.</blockquote>", parse_mode=ParseMode.HTML)

async def del_fsub_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menghapus channel dari FSub."""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("<blockquote>❌ Mohon sertakan ID channel yang ingin dihapus. Contoh:\n<code>/delfsubchannel -100123456789</code></blockquote>", parse_mode=ParseMode.HTML)
        return

    channel_id_str = context.args[0]
    try:
        channel_id = int(channel_id_str)
        if channel_id in config.get("fsub_channels", []):
            config["fsub_channels"].remove(channel_id)
            save_config(config)
            await update.message.reply_text(f"<blockquote>✅ Channel dengan ID {channel_id} berhasil dihapus dari daftar FSub.</blockquote>", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("<blockquote>❌ Channel tidak ditemukan di daftar FSub.</blockquote>", parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("<blockquote>❌ ID channel tidak valid. Pastikan itu adalah angka.</blockquote>", parse_mode=ParseMode.HTML)

async def list_fsub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan daftar channel dan tombol FSub."""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
    
    channel_list = "\n".join([f"• <code>{id}</code>" for id in config.get("fsub_channels", [])])
    button_list = "\n".join([f"• {btn['text']} | <code>{btn['url']}</code>" for btn in config.get("fsub_buttons", [])])
    
    message = f"<b>🔊 Daftar Channel FSub:</b>\n{channel_list or 'Tidak ada channel.'}\n\n<b>🔊 Daftar Tombol FSub:</b>\n{button_list or 'Tidak ada tombol.'}"
    await update.message.reply_text(f"<blockquote>{message}</blockquote>", parse_mode=ParseMode.HTML)

async def add_fsub_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menambahkan tombol FSub baru. (SUDAH DIPERBAIKI UNTUK TEKS MULTI-KATA)"""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
    if len(context.args) < 2:
        await update.message.reply_text("<blockquote>❌ Mohon sertakan teks dan URL tombol. Contoh:\n<code>/addfsubbutton Gabung Channel https://t.me/contohchannel</code></blockquote>", parse_mode=ParseMode.HTML)
        return

    button_text = " ".join(context.args[:-1])
    button_url = context.args[-1]

    config["fsub_buttons"].append({"text": button_text, "url": button_url})
    save_config(config)

    await update.message.reply_text(f"<blockquote>✅ Tombol FSub '{html.escape(button_text)}' berhasil ditambahkan.</blockquote>", parse_mode=ParseMode.HTML)

async def del_fsub_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menghapus tombol FSub berdasarkan teks. (SUDAH DIPERBAIKI UNTUK TEKS MULTI-KATA)"""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("<blockquote>❌ Mohon sertakan teks tombol yang ingin dihapus. Contoh:\n<code>/delfsubbutton Gabung Channel</code></blockquote>", parse_mode=ParseMode.HTML)
        return

    button_text_to_delete = " ".join(context.args)
    
    initial_count = len(config.get("fsub_buttons", []))
    config["fsub_buttons"] = [
        btn for btn in config["fsub_buttons"]
        if btn["text"] != button_text_to_delete
    ]
    
    if len(config["fsub_buttons"]) < initial_count:
        save_config(config)
        await update.message.reply_text(f"<blockquote>✅ Tombol FSub '{html.escape(button_text_to_delete)}' berhasil dihapus.</blockquote>", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("<blockquote>❌ Tombol FSub '{html.escape(button_text_to_delete)}' tidak ditemukan.</blockquote>", parse_mode=ParseMode.HTML)
    
async def set_welcome_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /setwelcome."""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
        
    reply_message = update.message.reply_to_message
    if not reply_message or not reply_message.text:
        await update.message.reply_text("<blockquote>⚙️ Mohon balas pesan teks yang ingin Anda jadikan pesan sambutan.</blockquote>", parse_mode=ParseMode.HTML)
        return

    new_message = reply_message.text
    config["welcome_message"] = new_message
    save_config(config)

    await update.message.reply_text(f"<blockquote>✅ Pesan sambutan berhasil diubah menjadi:\n\n{html.escape(new_message)}</blockquote>", parse_mode=ParseMode.HTML)

async def set_profile_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /getprofil."""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
    
    reply_message = update.message.reply_to_message
    if not reply_message or not reply_message.photo:
        await update.message.reply_text("<blockquote>❌ Mohon balas sebuah gambar dengan perintah /getprofil untuk mengatur gambar profil.</blockquote>", parse_mode=ParseMode.HTML)
        return
    file_id = reply_message.photo[-1].file_id
    config["photo_id"] = file_id
    save_config(config)
    caption_text = "<blockquote>✅ Gambar sambutan berhasil diatur!</blockquote>"
    await update.message.reply_photo(photo=file_id, caption=caption_text, parse_mode=ParseMode.HTML)

async def add_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /addvideo."""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return
        
    reply_message = update.message.reply_to_message
    if not reply_message or not reply_message.video:
        await update.message.reply_text("<blockquote>⚙️ Mohon balas video dengan perintah /addvideo &lt;nama_video&gt;.</blockquote>", parse_mode=ParseMode.HTML)
        return
    if not context.args:
        await update.message.reply_text("<blockquote>⚙️ Mohon berikan nama untuk video ini. Contoh: <code>/addvideo video_utama</code></blockquote>", parse_mode=ParseMode.HTML)
        return
    parameter_name = context.args[0]
    file_id = reply_message.video.file_id
    config["videos"][parameter_name] = file_id
    save_config(config)
    
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    message_text = f"<blockquote>✅ Video <code>{html.escape(parameter_name)}</code> telah disimpan!\nBagikan dengan link: <code>https://t.me/{html.escape(bot_username)}?start={html.escape(parameter_name)}</code></blockquote>"
    await update.message.reply_text(message_text, parse_mode=ParseMode.HTML)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mengirim broadcast ke semua pengguna."""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return

    reply_message = update.message.reply_to_message
    if not reply_message:
        await update.message.reply_text("<blockquote>⚙️ Mohon balas pesan yang ingin Anda broadcast.</blockquote>", parse_mode=ParseMode.HTML)
        return

    user_ids = set(config.get("user_ids", []))
    sent_count = 0
    blocked_count = 0
    
    logging.info(f"Memulai broadcast ke {len(user_ids)} pengguna...")

    broadcast_parse_mode = getattr(reply_message, 'parse_mode', ParseMode.HTML)

    for user_id in list(user_ids):
        try:
            if reply_message.text:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=reply_message.text,
                    parse_mode=broadcast_parse_mode
                )
            elif reply_message.photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=reply_message.photo[-1].file_id,
                    caption=reply_message.caption,
                    parse_mode=broadcast_parse_mode
                )
            # Tambahkan elif untuk jenis media lain (video, audio, dll.) jika diperlukan
            sent_count += 1
        except Forbidden:
            logging.info(f"Pengguna {user_id} telah memblokir bot. Menghapus dari daftar.")
            user_ids.remove(user_id)
            blocked_count += 1
        except Exception as e:
            logging.error(f"Gagal mengirim pesan ke pengguna {user_id}: {e}")

    config["user_ids"] = list(user_ids)
    save_config(config)
    
    await update.message.reply_text(f"<blockquote>✅ Broadcast selesai!\n\n📢 Pesan terkirim: {sent_count}\n💣 Pengguna yang memblokir: {blocked_count}\n\n👤Jumlah pengguna aktif saat ini: {len(user_ids)}</blockquote>", parse_mode=ParseMode.HTML)

async def add_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menambahkan tombol inline pada pesan yang dibalas. (SUDAH DIPERBAIKI UNTUK TEKS MULTI-KATA)"""
    config = get_config()
    if update.effective_user.id not in config.get("admin_ids", []):
        await update.message.reply_text("<blockquote>❌ Perintah ini hanya untuk admin.</blockquote>", parse_mode=ParseMode.HTML)
        return

    reply_message = update.message.reply_to_message
    if not reply_message:
        await update.message.reply_text("<blockquote>⚙️ Mohon balas pesan yang ingin Anda tambahkan tombol.</blockquote>", parse_mode=ParseMode.HTML)
        return
        
    if len(context.args) < 2:
        await update.message.reply_text("<blockquote>⚙️ Mohon sertakan teks dan URL tombol. Contoh:\n<code>/addbutton Kunjungi Website https://google.com</code></blockquote>", parse_mode=ParseMode.HTML)
        return

    button_text = " ".join(context.args[:-1])
    button_url = context.args[-1]
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=button_url)]])
    
    message_parse_mode = getattr(reply_message, 'parse_mode', ParseMode.HTML)

    try:
        if reply_message.text:
            await update.message.reply_text(
                text=reply_message.text,
                reply_markup=keyboard,
                parse_mode=message_parse_mode
            )
        elif reply_message.photo:
            await update.message.reply_photo(
                photo=reply_message.photo[-1].file_id,
                caption=reply_message.caption or "",
                reply_markup=keyboard,
                parse_mode=message_parse_mode
            )
        elif reply_message.video:
            await update.message.reply_video(
                video=reply_message.video.file_id,
                caption=reply_message.caption or "",
                reply_markup=keyboard,
                parse_mode=message_parse_mode
            )
        else:
            await update.message.reply_text("<blockquote>❌ Tipe pesan ini tidak didukung.</blockquote>", parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Gagal mengirim pesan dengan tombol: {e}")
        await update.message.reply_text(f"<blockquote>❌ Terjadi kesalahan saat mengirim pesan dengan tombol: {html.escape(str(e))}</blockquote>", parse_mode=ParseMode.HTML)

# --- Fungsi Utama ---
def main():
    """Memulai bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Menambahkan semua handler perintah
    application.add_handler(CommandHandler("setup", setup_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addfsubchannel", add_fsub_channel))
    application.add_handler(CommandHandler("delfsubchannel", del_fsub_channel))
    application.add_handler(CommandHandler("listfsub", list_fsub))
    application.add_handler(CommandHandler("addfsubbutton", add_fsub_button))
    application.add_handler(CommandHandler("delfsubbutton", del_fsub_button))
    application.add_handler(CommandHandler("setwelcome", set_welcome_message_handler))
    application.add_handler(CommandHandler("getprofil", set_profile_photo_handler))
    application.add_handler(CommandHandler("addvideo", add_video_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("addbutton", add_button_handler))
    
    logging.info("🚀 Bot sedang berjalan...")
    application.run_polling(poll_interval=1)

if __name__ == "__main__":
    main()
