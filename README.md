# Telegram Torrent Bot

Lightweight Telegram bot to search via Jackett and add torrents to qBittorrent, with simple system status and post-download hooks.

## Setup
- Python 3.10+
- System tools: `curl`, `jq`, `systemd`

```bash
python3 -m venv mybotenv && source mybotenv/bin/activate
pip install -r requirements.txt
```

Create `bot/.env` with:

```
BOT_TOKEN=...
AUTHORIZED_USER_ID=...
ALLOWED_CHAT_ID=...
QB_URL=http://127.0.0.1:4545
QB_USER=admin
QB_PASS=adminadmin
# Optional
PLEX_SERVICE_NAME=plexmediaserver
JACKETT_CONFIG_PATH=/opt/telegrambot/config.json
# Jackett config via env (overrides JSON if set)
JACKETT_URL=http://127.0.0.1:9117
JACKETT_API_KEY=your_api_key_here
JACKETT_DEFAULT_INDEXER=all
```

Copy and fill `config.sample.json` to the path set in `JACKETT_CONFIG_PATH` (default `/opt/telegrambot/config.json`).
Alternatively, set `JACKETT_URL`, `JACKETT_API_KEY`, and `JACKETT_DEFAULT_INDEXER` in `.env`.

## Run
```bash
python -m bot.main
```

## Tests
```bash
./run_all_tests.sh
# or
PYTHONPATH=. pytest --cov=bot --cov-report=term --cov-report=html tests/
```

## Post-download hooks
Use scripts in `scripts/` from qBittorrent's "Run external program" hooks. Scripts source env from `scripts/.env`, `bot/.env`, or repo `.env`.
