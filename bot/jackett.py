import os
import requests
import json

CONFIG_PATH = os.getenv("JACKETT_CONFIG_PATH", "/opt/telegrambot/config.json")

def load_config() -> dict:
    """Load Jackett config from JSON file, overridden by env vars if set.

    Supports env keys: JACKETT_URL, JACKETT_API_KEY, JACKETT_DEFAULT_INDEXER.
    """
    cfg: dict = {}
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    # Overlay env vars if present
    env_url = os.getenv("JACKETT_URL")
    env_key = os.getenv("JACKETT_API_KEY")
    env_idx = os.getenv("JACKETT_DEFAULT_INDEXER")
    if env_url:
        cfg["jackett_url"] = env_url
    if env_key:
        cfg["jackett_api_key"] = env_key
    if env_idx:
        cfg["default_indexer"] = env_idx
    return cfg

def extract_magnet_from_link(link: str) -> str | None:
    try:
        res = requests.get(link, allow_redirects=False, timeout=5)
        if res.status_code in (301, 302):
            loc = res.headers.get("Location", "")
            if loc.startswith("magnet:"):
                return loc
    except Exception:
        pass
    return None

def search_torrents(query: str, max_results: int = 10) -> list[dict]:
    cfg = load_config()
    idx = cfg.get('default_indexer', '')
    jackett_url = (cfg.get('jackett_url', '') or '').rstrip('/')
    api_key = cfg.get('jackett_api_key', '')
    if not jackett_url or not api_key or not idx:
        return []
    url = f"{jackett_url}/api/v2.0/indexers/{idx}/results"
    params = {"apikey": api_key, "Query": query}
    try:
        resp = requests.get(url, params=params, timeout=8)
        items = resp.json().get("Results", [])
    except Exception:
        return []
    results = []
    for item in items:
        magnet = item.get("MagnetUri") or extract_magnet_from_link(item.get("Link", ""))
        if not magnet:
            continue
        results.append({
            "title": item.get("Title", ""),
            "size": item.get("Size", 0) // (1024 * 1024),
            "seeders": item.get("Seeders", 0),
            "tracker": item.get("Tracker", ""),
            "magnet": magnet
        })
        if len(results) >= max_results:
            break
    return results
