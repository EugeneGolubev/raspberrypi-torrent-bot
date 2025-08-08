
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot.handlers import _allowed, handle_message, handle_status
import types

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("AUTHORIZED_USER_ID", "123")
    monkeypatch.setenv("ALLOWED_CHAT_ID", "-100123")
    monkeypatch.setenv("BOT_TOKEN", "dummy")

@pytest.mark.asyncio
@pytest.mark.parametrize("chat_type,chat_id,user_id,expected", [
    ("private", 123, 123, True),
    ("group", -100123, 555, True),
    ("supergroup", -100123, 555, True),
    ("group", -100999, 555, False),
    ("private", 999, 999, False),
    ("channel", -1, 1, False),
])
async def test__allowed_behavior(monkeypatch, chat_type, chat_id, user_id, expected):
    assert _allowed(chat_type, chat_id, user_id) == expected

@pytest.mark.asyncio
async def test_handle_message_search(monkeypatch):
    mock_update = MagicMock()
    mock_update.effective_chat.type = "private"
    mock_update.effective_chat.id = 123
    mock_update.effective_user.id = 123
    mock_update.message.text = "test torrent"
    mock_update.message.reply_text = AsyncMock()

    mock_context = MagicMock()
    mock_context.user_data = {}

    monkeypatch.setattr("handlers._allowed", lambda *a: True)
    monkeypatch.setattr("bot.handlers.search_torrents", lambda q: [
        {
            "title": f"Torrent {i}",
            "size": 123,
            "seeders": 50,
            "tracker": "X",
            "magnet": "magnet:?xt=urn"
        } for i in range(3)
    ])
    monkeypatch.setattr("handlers.search_torrents", lambda q: [{
        "title": "Test",
        "size": 123,
        "seeders": 50,
        "tracker": "X",
        "magnet": "magnet:?xt=urn"
    }] * 3)
    monkeypatch.setattr("handlers.send_search_page", AsyncMock())

    await handle_message(mock_update, mock_context)
    assert mock_context.user_data["search_page"] == 0
    assert len(mock_context.user_data["search_results"]) == 3

@pytest.mark.asyncio
async def test_handle_status(monkeypatch):
    update = MagicMock()
    update.effective_chat.type = "private"
    update.effective_chat.id = 123
    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()

    context = MagicMock()

    monkeypatch.setattr("handlers._allowed", lambda *a: True)
    monkeypatch.setattr("handlers.qb_list_torrents", lambda: [{"state": "downloading", "progress": 0.5}])
    monkeypatch.setattr("handlers.qb_list_pending_torrents", lambda limit=None, count_only=True: 1)
    monkeypatch.setattr("handlers.check_url_status", lambda u: "✅ Online")
    monkeypatch.setattr("handlers.check_service", lambda s: "✅ Running")
    monkeypatch.setattr("handlers.check_telegram_api", lambda token: "✅ Online")
    monkeypatch.setattr("handlers.get_disk_space", lambda: "42 GB free")
    monkeypatch.setattr("handlers.get_ram_usage", lambda: "1024 MB / 4096 MB")
    monkeypatch.setattr("handlers.get_cpu_usage", lambda: "20.0% (Load: 0.5, 0.2)")

    await handle_status(update, context)
    update.message.reply_text.assert_awaited()
