import os
import json
import logging
from pyrogram import Client, filters

ADMIN_ID = int(os.getenv("ADMIN_ID"))

def get_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def get_video_list():
    try:
        with open("videos.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_video_list(video_list):
    with open("videos.json", "w") as f:
        json.dump(video_list, f, indent=4)

def get_buttons_list():
    try:
        with open("buttons.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_buttons_list(buttons_list):
    with open("buttons.json", "w") as f:
        json.dump(buttons_list, f, indent=4)

@Client.on_message(filters.user(ADMIN_ID) & filters.private & filters.command("setchannel", prefixes="/"))
async def set_channel_handler(client, message):
    if len(message.command) < 3:
        await message.reply_text("❌ Format salah. Contoh: /setchannel -100123456789 https://t.me/nama_channel")
        return
    
    try:
        channel_id = int(message.command[1])
        channel_link = message.command[2]
    except (ValueError, IndexError):
        await message.reply_text("❌ Format ID channel atau link salah.")
        return
        
    config = get_config()
    config["channel_id"] = channel_id
    config["channel_link"] = channel_link
    save_config(config)
    
    await message.reply_text("✅ Channel ID dan link berhasil diperbarui.")

@Client.on_message(filters.user(ADMIN_ID) & filters.private & filters.command("addvideo", prefixes="/"))
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
        f"✅ Video `{parameter_name}` telah disimpan! "
        f"Bagikan dengan link: `https://t.me/{client.me.username}?start={parameter_name}`"
    )
    logging.info(f"Admin menambahkan video baru: {parameter_name}")

@Client.on_message(filters.user(ADMIN_ID) & filters.private & filters.command("addbutton", prefixes="/"))
async def add_button_handler(client, message):
    if len(message.command) < 3:
        await message.reply_text("❌ Mohon berikan teks dan URL. Contoh: `/addbutton Website https://contoh.com`")
        return
    button_text = " ".join(message.command[1:-1])
    button_url = message.command[-1]
    buttons_list = get_buttons_list()
    buttons_list.append({"text": button_text, "url": button_url})
    save_buttons_list(buttons_list)
    await message.reply_text(f"✅ Tombol '{button_text}' telah ditambahkan.")

@Client.on_message(filters.user(ADMIN_ID) & filters.private & filters.command("listbuttons", prefixes="/"))
async def list_buttons_handler(client, message):
    buttons_list = get_buttons_list()
    if not buttons_list:
        await message.reply_text("Tidak ada tombol yang tersimpan.")
        return
    response = "Daftar Tombol:\n\n"
    for btn in buttons_list:
        response += f"- Teks: `{btn['text']}`\n- URL: `{btn['url']}`\n\n"
    await message.reply_text(response)

@Client.on_message(filters.user(ADMIN_ID) & filters.private & filters.command("delbutton", prefixes="/"))
async def del_button_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Mohon berikan teks tombol yang ingin dihapus. Contoh: `/delbutton Website`")
        return
    button_text_to_delete = " ".join(message.command[1:])
    buttons_list = get_buttons_list()
    new_buttons_list = [btn for btn in buttons_list if btn['text'] != button_text_to_delete]
    if len(new_buttons_list) == len(buttons_list):
        await message.reply_text("❌ Tombol dengan teks tersebut tidak ditemukan.")
    else:
        save_buttons_list(new_buttons_list)
        await message.reply_text(f"✅ Tombol '{button_text_to_delete}' telah dihapus.")
