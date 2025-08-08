#!/bin/bash

# Log the torrent name
$(dirname "$0")/notify_complete.sh "$1"

# Optional: Wait for file to be fully flushed
sleep 10

# Run deletion script as qbtuser
$(dirname "$0")/delete_completed.sh

echo "$(date): Finished $1" >> $(dirname "$0")/post_download.log
