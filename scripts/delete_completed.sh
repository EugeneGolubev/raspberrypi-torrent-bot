#!/bin/bash

HOST="http://127.0.0.1:4545"
USERNAME="admin"
PASSWORD="adminadmin"
COOKIE_FILE="$(dirname "$0")/cookies.txt"

# Authenticate
curl -s -c "$COOKIE_FILE" -d "username=$USERNAME&password=$PASSWORD" "$HOST/api/v2/auth/login"

# Get completed torrents and delete them
curl -s -b "$COOKIE_FILE" "$HOST/api/v2/torrents/info" |
jq -r '.[] | select(.progress == 1.0) | .hash' |
while read -r hash; do
    echo "😏 Torrent completed: $hash — giving it 1 minute to bask in glory..."
    sleep 15
    echo "🔥 Deleting: $hash"
    curl -s -X POST -b "$COOKIE_FILE" -d "hashes=$hash&deleteFiles=false" "$HOST/api/v2/torrents/delete"
done
