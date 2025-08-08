
import pytest
from unittest.mock import patch, mock_open, MagicMock
import bot.jackett as jackett

def test_load_config_valid(monkeypatch):
    mock_data = '{"jackett_url": "http://localhost:9117", "jackett_api_key": "abc123", "default_indexer": "test"}'
    monkeypatch.setattr("builtins.open", mock_open(read_data=mock_data))
    result = jackett.load_config()
    assert result["jackett_url"] == "http://localhost:9117"

def test_load_config_missing(monkeypatch):
    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(FileNotFoundError()))
    result = jackett.load_config()
    assert result == {}

def test_extract_magnet_from_link_redirect(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 302
    mock_resp.headers = {"Location": "magnet:?xt=urn:btih:example"}
    monkeypatch.setattr("requests.get", lambda *a, **kw: mock_resp)

    result = jackett.extract_magnet_from_link("http://dummy")
    assert result.startswith("magnet:")

def test_extract_magnet_from_link_fail(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    monkeypatch.setattr("requests.get", lambda *a, **kw: mock_resp)

    result = jackett.extract_magnet_from_link("http://dummy")
    assert result is None

def test_search_torrents_success(monkeypatch):
    fake_results = [{
        "Title": "Test Torrent",
        "Size": 104857600,
        "Seeders": 100,
        "Tracker": "tracker1",
        "MagnetUri": "magnet:?xt=urn:btih:test"
    }]
    mock_config = {
        "jackett_url": "http://localhost:9117",
        "jackett_api_key": "key",
        "default_indexer": "indexer"
    }

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"Results": fake_results}
    mock_resp.status_code = 200

    monkeypatch.setattr(jackett, "load_config", lambda: mock_config)
    monkeypatch.setattr("requests.get", lambda *a, **kw: mock_resp)

    results = jackett.search_torrents("test")
    assert len(results) == 1
    assert results[0]["title"] == "Test Torrent"
