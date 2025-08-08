import requests
import os

QB_URL  = os.getenv("QB_URL", "http://127.0.0.1:4545").rstrip("/")
QB_USER = os.getenv("QB_USER", "")
QB_PASS = os.getenv("QB_PASS", "")

_session = requests.Session()

def _ensure_logged_in() -> bool:
    """
    Login only if there is no SID cookie or last login likely expired.
    """
    try:
        # If we already have a SID cookie, assume we are logged in
        if "SID" in _session.cookies.get_dict():
            return True
        r = _session.post(
            f"{QB_URL}/api/v2/auth/login",
            data={"username": QB_USER, "password": QB_PASS},
            timeout=5,
        )
        return r.status_code == 200 and "SID" in _session.cookies.get_dict()
    except Exception:
        return False

def add_torrent(magnet: str, category: str | None = None) -> bool:
    """
    Add a magnet to qBittorrent, optional category.
    """
    if not magnet or not magnet.startswith("magnet:"):
        return False
    if not _ensure_logged_in():
        return False
    data = {"urls": magnet}
    if category:
        data["category"] = category
    try:
        _session.post(f"{QB_URL}/api/v2/torrents/add", data=data, timeout=5)
        return True
    except Exception:
        return False

def qb_list_torrents() -> list[dict]:
    """
    Return list of torrents with their states.
    """
    if not _ensure_logged_in():
        return []
    try:
        r = _session.get(f"{QB_URL}/api/v2/torrents/info", timeout=5)
        return r.json() if r.ok else []
    except Exception:
        return []

def qb_health() -> bool:
    """
    Lightweight check that auth + API works.
    """
    if not _ensure_logged_in():
        return False
    try:
        r = _session.get(f"{QB_URL}/api/v2/app/version", timeout=5)
        return r.ok
    except Exception:
        return False
