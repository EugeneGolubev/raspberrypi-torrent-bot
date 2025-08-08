#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"      # /opt/telegrambot
BOT_ENV_PATH="$PROJECT_ROOT/bot/.env"
ROOT_ENV_PATH="$PROJECT_ROOT/.env"

# Load .env
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
elif [ -f "$BOT_ENV_PATH" ]; then
    source "$BOT_ENV_PATH"
elif [ -f "$ROOT_ENV_PATH" ]; then
    source "$ROOT_ENV_PATH"
else
    echo "❌ .env file not found in:"
    echo "   $SCRIPT_DIR/.env"
    echo "   $BOT_ENV_PATH"
    echo "   $ROOT_ENV_PATH"
    exit 1
fi

# Now we can safely use env vars (QB_URL, QB_USER, QB_PASS)
HOST="$QB_URL"
USERNAME="$QB_USER"
PASSWORD="$QB_PASS"
COOKIE_FILE="$SCRIPT_DIR/cookies.txt"

# Authenticate
curl -s -c "$COOKIE_FILE" -d "username=$USERNAME&password=$PASSWORD" "$HOST/api/v2/auth/login"

# Get completed torrents and delete them (but keep files)
curl -s -b "$COOKIE_FILE" "$HOST/api/v2/torrents/info" |
jq -r '.[] | select(.progress == 1.0) | .hash' |
while read -r hash; do
    echo "😏 Torrent completed: $hash — giving it 15 seconds before deletion..."
    sleep 15
    echo "🔥 Deleting: $hash"
    curl -s -X POST -b "$COOKIE_FILE" \
         -d "hashes=$hash&deleteFiles=false" \
         "$HOST/api/v2/torrents/delete"
done
