import json
import logging
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_ID = int(os.getenv("ADMIN_ID"))

def get_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_video_list():
    try:
        with open("videos.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_buttons_list():
    try:
        with open("buttons.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

async def check_subscription(client: Client, user_id: int, channel_id: int):
    logging.info(f"Mengecek langganan pengguna {user_id} di channel {channel_id}...")
    try:
        member_status = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
        logging.info(f"Status anggota: {member_status.status}")
        return member_status.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logging.error(f"Error saat memeriksa langganan: {e}")
        return False

@Client.on_message(filters.command("start", prefixes="/"))
async def start_command(client, message):
    config = get_config()
    channel_id = config.get("channel_id")
    channel_link = config.get("channel_link")
    
    if not channel_id or not channel_link:
        if message.from_user.id == ADMIN_ID:
            await message.reply_text("❌ Channel ID atau link belum diatur. Mohon gunakan perintah /setchannel.")
        else:
            await message.reply_text("❌ Bot belum sepenuhnya dikonfigurasi. Mohon coba lagi nanti.")
        return

    user_id = message.from_user.id
    start_parameter = message.command[1] if len(message.command) > 1 else None
    
    is_subscribed = await check_subscription(client, user_id, channel_id)
    
    if not is_subscribed:
        pesan = "❌ Anda belum bergabung ke channel kami.\n\nSilakan bergabung ke channel di bawah ini untuk bisa menggunakan bot ini."
        
        keyboard_buttons = []
        keyboard_buttons.append([InlineKeyboardButton("Gabung Channel", url=channel_link)])
        
        custom_buttons = get_buttons_list()
        for btn in custom_buttons:
            keyboard_buttons.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
        
        coba_lagi_link = f"https://t.me/{client.me.username}?start={start_parameter or ''}"
        keyboard_buttons.append([InlineKeyboardButton("Coba Lagi", url=coba_lagi_link)])
        
        keyboard = InlineKeyboardMarkup(keyboard_buttons)
        await message.reply_text(pesan, reply_markup=keyboard)
    else:
        video_list = get_video_list()
        
        if not start_parameter:
            await message.reply_text(
                "✅ Anda sudah bergabung. Gunakan link /start dengan parameter yang valid."
            )
            return

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

@Client.on_message(filters.command("myid", prefixes="/"))
async def my_id_command(client, message):
    user_id = message.from_user.id
    await message.reply_text(f"User ID Anda adalah: `{user_id}`")
