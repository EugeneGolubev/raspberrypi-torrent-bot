import asyncio
import os
import shutil
import subprocess
import psutil
import requests
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, ContextTypes, filters
from jackett import search_torrents
from torrent import qb_login, qb_list_torrents
from utils import get_disk_space, get_ram_usage, get_cpu_usage, check_service, check_url_status, check_telegram_api
from handlers import handle_message, handle_category_selection, handle_status, handle_tstatus
from dotenv import load_dotenv

# === Configuration ===
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("ALLOWED_CHAT_ID"))
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))

QB_URL = "http://127.0.0.1:4545"
QB_USER = "admin"
QB_PASS = "adminadmin"
CONFIG_PATH = "/home/pi-user/config.json"

session = requests.Session()


# === Bot Startup ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("tstatus", handle_tstatus))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_category_selection))
    app.run_polling()
