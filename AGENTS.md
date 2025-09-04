# Repository Guidelines

## Project Structure & Module Organization
- `bot/`: Telegram bot code (`main.py`, `handlers.py`, `jackett.py`, `torrent.py`, `utils.py`). Loads env from `bot/.env`.
- `tests/`: Pytest suite covering handlers, Jackett, torrent, and utils.
- `scripts/`: Shell helpers run by qBittorrent post-download hooks (`notify_complete.sh`, `delete_completed.sh`, `run_post_download.sh`).
- `config.json`: Jackett settings read by `bot/jackett.py` (path: `/opt/telegrambot/config.json`).
- `requirements.txt`, `run_all_tests.sh`: Python deps and test runner.

## Build, Test, and Development Commands
- Create venv: `python3 -m venv mybotenv && source mybotenv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Run bot: `python -m bot.main` (requires `bot/.env` with tokens and IDs)
- Run tests + coverage: `./run_all_tests.sh` or `PYTHONPATH=. pytest --cov=bot --cov-report=term --cov-report=html tests/`

## Coding Style & Naming Conventions
- Python, PEP 8, 4-space indent; prefer f-strings and `logging`.
- Use snake_case for files, functions, and variables; PascalCase for classes.
- Type hints where practical (public functions and return types in new code).
- No formatter is enforced; if you use one, keep diffs minimal.

## Testing Guidelines
- Framework: Pytest (see files in `tests/`).
- Name tests `tests/test_*.py`; keep unit tests hermetic (monkeypatch network/process calls).
- Aim for ≥80% coverage on touched modules; update or add tests with clear arrange/act/assert sections.
- Run `pytest -k name_substring` for focused runs during development.

## Commit & Pull Request Guidelines
- Commit messages: imperative mood, concise subject (≤72 chars), optional body explaining why.
- Prefer Conventional Commits where natural: `feat:`, `fix:`, `chore:`, `test:`, `docs:`.
- PRs should include: summary, linked issues, test evidence (logs or screenshots), and any config changes (`.env` keys, `config.json`).
- Keep changes scoped; update tests and docs in the same PR when behavior changes.

## Security & Configuration Tips
- Never commit secrets. `.env` and logs are ignored; keep tokens in `bot/.env` or a root `.env`.
- Required env keys: `BOT_TOKEN`, `AUTHORIZED_USER_ID`, `ALLOWED_CHAT_ID`; qBittorrent: `QB_URL`, `QB_USER`, `QB_PASS`; optional `PLEX_SERVICE_NAME`.
- Scripts source env from `scripts/.env`, `bot/.env`, or repo `.env`. Validate with `echo $BOT_TOKEN` before running.
