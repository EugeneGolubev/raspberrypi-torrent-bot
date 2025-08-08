#!/bin/bash
BOT_TOKEN="8214598860:AAGfd1_8or7peXppHgkyekOV4oArXc_1Ezo"
CHAT_ID="93992596"
TORRENT_NAME="$1"

MESSAGE="🔥 Torrent completed: $TORRENT_NAME"
curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
     -d chat_id="$CHAT_ID" \
     -d text="$MESSAGE"
