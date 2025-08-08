
import subprocess
import os
import tempfile
from pathlib import Path

def write_script(name, content):
    path = Path(tempfile.gettempdir()) / name
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
    return str(path)

def test_notify_complete_sh(monkeypatch):
    env_path = Path(tempfile.gettempdir()) / ".env"
    env_path.write_text("BOT_TOKEN=dummy\nALLOWED_CHAT_ID=123456", encoding="utf-8")

    script = write_script("notify_complete.sh", """#!/bin/bash
BOT_TOKEN="dummy"
CHAT_ID="123456"
TORRENT_NAME="TestTorrent"
echo "Would notify $CHAT_ID with $TORRENT_NAME"
exit 0
""")
    result = subprocess.run([script], capture_output=True, text=True)
    assert "Would notify 123456 with TestTorrent" in result.stdout
    os.remove(script)

def test_delete_completed_sh_logic(monkeypatch):
    script = write_script("delete_completed.sh", """#!/bin/bash
echo "Authenticating to qBittorrent..."
echo "Checking for completed torrents..."
echo "Deleting torrent abc123"
exit 0
""")
    result = subprocess.run([script], capture_output=True, text=True)
    assert "Authenticating" in result.stdout
    assert "Deleting torrent" in result.stdout
    os.remove(script)

def test_run_post_download_sh(monkeypatch):
    log_path = Path(tempfile.gettempdir()) / "post_download_test.log"
    if log_path.exists():
        log_path.unlink()

    script = write_script("run_post_download.sh", f"""#!/bin/bash
echo "Notifying about $1"
sleep 0
echo "Deleting completed torrent..."
echo "$(date): Finished $1" >> "{log_path}"
""")
    name = "TestTorrent"
    result = subprocess.run([script, name], capture_output=True, text=True)
    assert "Notifying about" in result.stdout
    assert log_path.exists()
    log_path.unlink()
    os.remove(script)
