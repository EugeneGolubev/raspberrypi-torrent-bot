import os
import logging
from pathlib import Path
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, filters, Defaults
from bot.handlers import handle_message, handle_category_selection, handle_status, handle_tstatus
from dotenv import load_dotenv

# Always load .env sitting next to main.py (CWD-independent)
load_dotenv(dotenv_path=Path(__file__).with_name('.env'))

BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USER_ID = os.getenv("AUTHORIZED_USER_ID")
ALLOWED_CHAT_ID = os.getenv("ALLOWED_CHAT_ID")

# Fail loudly if missing
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in .env")
if not AUTHORIZED_USER_ID or not ALLOWED_CHAT_ID:
    raise RuntimeError("AUTHORIZED_USER_ID or ALLOWED_CHAT_ID missing in .env")

# Cast after presence check
AUTHORIZED_USER_ID = int(AUTHORIZED_USER_ID)
ALLOWED_CHAT_ID = int(ALLOWED_CHAT_ID)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .defaults(Defaults(parse_mode=ParseMode.MARKDOWN))
        .build()
    )
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("tstatus", handle_tstatus))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_category_selection))
    app.run_polling()
