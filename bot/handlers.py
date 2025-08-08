import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import get_disk_space, get_ram_usage, get_cpu_usage, check_service, check_url_status, check_telegram_api
from torrent import qb_list_torrents, qb_login
from jackett import search_torrents
from torrent import add_torrent


# Use your AUTHORIZED_USER_ID, ALLOWED_CHAT_ID, BOT_TOKEN as needed
AUTHORIZED_USER_ID = 93992596
ALLOWED_CHAT_ID = -4979329913
BOT_TOKEN = "8214598860:AAGfd1_8or7peXppHgkyekOV4oArXc_1Ezo"

pending_links = {}

async def send_search_page(msg, context):
    page = context.user_data.get("search_page", 0)
    results = context.user_data.get("search_results", [])
    per = 10
    total = len(results)
    pages = (total + per - 1) // per
    start = page * per
    subset = results[start:start+per]

    chat_type = msg.message.chat.type
    delay = 0.1 if chat_type == "private" else 1.0  # Slower delay for group/supergroup

    print(f"[DEBUG] Sending search page {page+1} in {chat_type} with delay {delay}s")

    for i, t in enumerate(subset, start=start):
        text = (
            f"🎬 *{i+1}. {t['title']}*\n"
            f"📦 {t['size']} MB | 👥 {t['seeders']} | 🌍 `{t['tracker']}`"
        )
        await msg.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Get Magnet", callback_data=f"magnet_{i}")]]
            )
        )
        await asyncio.sleep(delay)

    kb = []
    if page > 0:
        kb.append(InlineKeyboardButton("⬆️ Prev", callback_data="page_prev"))
    if start + per < total:
        kb.append(InlineKeyboardButton("⬇️ Next", callback_data="page_next"))
    info = f"Page {page+1}/{pages} ({total} results)"
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(info, callback_data="noop")]] + ([kb] if kb else [])
    )
    await msg.message.reply_text("Navigate:", reply_markup=markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    uid = update.effective_user.id
    if (chat.type == "private" and uid != AUTHORIZED_USER_ID) or \
       (chat.type in ("group","supergroup") and chat.id != ALLOWED_CHAT_ID):
        return
    text = update.message.text.strip()
    if text.startswith("magnet:"):
        context.user_data['pending'] = text
        kb = [[InlineKeyboardButton(c, callback_data=c)] for c in ("Movie","TV","Others")]
        await update.message.reply_text("Choose category:", reply_markup=InlineKeyboardMarkup(kb))
        return
    results = search_torrents(text)
    if not results:
        await update.message.reply_text("😕 No torrents found.")
        return
    context.user_data['search_results'], context.user_data['search_page'] = results, 0
    await send_search_page(update, context)

async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    chat = q.message.chat
    uid = q.from_user.id
    if (chat.type == "private" and uid != AUTHORIZED_USER_ID) or \
       (chat.type in ("group","supergroup") and chat.id != ALLOWED_CHAT_ID):
        return
    if data == "noop":
        return

    if data in ("page_prev", "page_next"):
        context.user_data["search_page"] += 1 if data == "page_next" else -1
        await q.message.delete()
        await send_search_page(q, context)
        return

    if data.startswith("magnet_"):
        index = int(data.split("_")[1])
        results = context.user_data.get("search_results", [])
        if index < len(results):
            pending_links[uid] = results[index]["magnet"]
            kb = [[InlineKeyboardButton(c, callback_data=c)] for c in ("Movie", "TV", "Others")]
            await q.edit_message_text("Select category:", reply_markup=InlineKeyboardMarkup(kb))
        return
    # add torrent
    magnet = pending_links.get(uid)
    if not magnet:
        await q.edit_message_text("No magnet link.")
        return
    if not add_torrent(magnet, data):
        await q.edit_message_text("❌ qBittorrent login failed.")
        return
    await q.edit_message_text(f"✅ Added as *{data}*", parse_mode="Markdown")
    pending_links.pop(uid, None)
    context.user_data.pop('pending', None)


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    uid = update.effective_user.id
    if (chat.type == "private" and uid != AUTHORIZED_USER_ID) or \
       (chat.type in ("group","supergroup") and chat.id != ALLOWED_CHAT_ID):
        return
    # qB stats
    qbt_status = "✅ Connected"
    downloading = paused = completed = 0
    torrents = qb_list_torrents()
    for t in torrents:
        if t.get('state')=='downloading': downloading+=1
        if t.get('state')=='pausedUP': paused+=1
        if t.get('progress',0)==1.0: completed+=1
    # services
    jackett_webui = check_url_status("http://127.0.0.1:9117")
    jackett_service = check_service("jackett")
    tg_api = check_telegram_api(BOT_TOKEN)
    tg_service = check_service("telegrambot")
    # system
    disk = get_disk_space()
    ram = get_ram_usage()
    cpu = get_cpu_usage()
    text = (
        "*📊 System Status*\n"
        "```\n"
        "=== qBittorrent ===\n"
        f"🔌 {qbt_status}\n"
        f"⬇️  Downloading: {downloading}\n"
        f"⏸️  Paused:      {paused}\n"
        f"✅ Completed:   {completed}\n\n"
        "=== Jackett ===\n"
        f"🌐 WebUI:   {jackett_webui}\n"
        f"🧲 Service: {jackett_service}\n\n"
        "=== Telegram Bot ===\n"
        f"📡 API:     {tg_api}\n"
        f"🛎️ Service: {tg_service}\n\n"
        "=== System ===\n"
        f"💽 Disk:     {disk}\n"
        f"🧠 RAM:      {ram}\n"
        f"⚙️ CPU:      {cpu}\n"
        "```"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_tstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    uid = update.effective_user.id
    if (chat.type == "private" and uid != AUTHORIZED_USER_ID) or \
       (chat.type in ("group","supergroup") and chat.id != ALLOWED_CHAT_ID):
        return
    ts = qb_list_torrents()
    if not ts:
        await update.message.reply_text("No torrents or failed to fetch.")
        return
    msg = "*📋 Torrent Status*\n```"
    for t in ts:
        name = t.get('name')[:30]
        state = t.get('state')
        msg += f"{name:30} | {state}\n"
    msg += "```"
    await update.message.reply_text(msg, parse_mode="Markdown")
