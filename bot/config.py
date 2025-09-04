from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    bot_token: str
    authorized_user_id: int
    allowed_chat_id: int
    plex_service_name: str

    qb_url: str
    qb_user: str
    qb_pass: str

    jackett_config_path: str


def get_settings() -> Settings:
    """Load settings from environment every call.

    Keeping this simple (no caching) helps tests that monkeypatch env.
    """
    bot_token = os.getenv("BOT_TOKEN", "")
    try:
        authorized_user_id = int(os.getenv("AUTHORIZED_USER_ID", "0"))
    except ValueError:
        authorized_user_id = 0
    try:
        allowed_chat_id = int(os.getenv("ALLOWED_CHAT_ID", "0"))
    except ValueError:
        allowed_chat_id = 0

    plex_service_name = os.getenv("PLEX_SERVICE_NAME", "plexmediaserver")

    qb_url = os.getenv("QB_URL", "http://127.0.0.1:4545").rstrip("/")
    qb_user = os.getenv("QB_USER", "")
    qb_pass = os.getenv("QB_PASS", "")

    jackett_config_path = os.getenv(
        "JACKETT_CONFIG_PATH",
        str(Path("/opt/telegrambot") / "config.json"),
    )

    return Settings(
        bot_token=bot_token,
        authorized_user_id=authorized_user_id,
        allowed_chat_id=allowed_chat_id,
        plex_service_name=plex_service_name,
        qb_url=qb_url,
        qb_user=qb_user,
        qb_pass=qb_pass,
        jackett_config_path=jackett_config_path,
    )

