import requests

QB_URL = "http://127.0.0.1:4545"
QB_USER = "admin"
QB_PASS = "adminadmin"

session = requests.Session()

def add_torrent(magnet, category):
    if not qb_login():
        return False
    session.post(f"{QB_URL}/api/v2/torrents/add", data={"urls": magnet, "category": category})
    return True

def qb_login() -> bool:
    try:
        r = session.post(f"{QB_URL}/api/v2/auth/login", data={"username": QB_USER, "password": QB_PASS})
        return r.status_code == 200 and "SID" in session.cookies.get_dict()
    except Exception:
        return False

def qb_list_torrents() -> list[dict]:
    if not qb_login():
        return []
    try:
        r = session.get(f"{QB_URL}/api/v2/torrents/info")
        return r.json()
    except Exception:
        return []
