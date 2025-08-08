import requests
import json

CONFIG_PATH = "/opt/telegrambot/config.json"

def load_config() -> dict:
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}

def extract_magnet_from_link(link: str) -> str | None:
    try:
        res = requests.get(link, allow_redirects=False)
        if res.status_code in (301, 302):
            loc = res.headers.get("Location", "")
            if loc.startswith("magnet:"):
                return loc
    except Exception:
        pass
    return None

def search_torrents(query: str, max_results: int = 40) -> list[dict]:
    cfg = load_config()
    idx = cfg.get('default_indexer', '')
    url = f"{cfg.get('jackett_url', '')}/api/v2.0/indexers/{idx}/results"
    params = {"apikey": cfg.get('jackett_api_key', ''), "Query": query}
    try:
        resp = requests.get(url, params=params)
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
