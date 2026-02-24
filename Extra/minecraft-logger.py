import os
import time
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ================== CONFIG ==================
LOG_PATH = "/srv/minecraft/vanilla/logs/latest.log"  # CHANGE IF NEEDED
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1466388938531930125/UF-K6Y-3BpZk-082Gdnj58H6ocLwgy7d0rLFOguTf8hJysjiMhkkgvm1eQ7SCLbjCWYC"
POLL_INTERVAL = 0.25  # seconds
# ============================================

JOIN_RE  = re.compile(r"\]: (.+?) joined the game\b")
LEAVE_RE = re.compile(r"\]: (.+?) left the game\b")


def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def send_discord(session: requests.Session, message: str) -> None:
    if not DISCORD_WEBHOOK_URL or "PASTE_NEW_WEBHOOK_HERE" in DISCORD_WEBHOOK_URL:
        print("Discord webhook not set")
        return

    try:
        r = session.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)

        if r.status_code == 429:
            retry_after = r.json().get("retry_after", 2)
            time.sleep(float(retry_after))
            session.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)

    except Exception as e:
        print("Discord webhook failed:", e)


def follow_latest_log(path: str):
    inode = None
    f = None

    while True:
        try:
            st = os.stat(path)

            # log rotated or first open
            if f is None or inode != st.st_ino:
                if f:
                    f.close()
                f = open(path, "r", encoding="utf-8", errors="replace")
                f.seek(0, os.SEEK_END)
                inode = st.st_ino

            line = f.readline()
            if line:
                yield line.rstrip("\n")
            else:
                time.sleep(POLL_INTERVAL)

        except FileNotFoundError:
            time.sleep(1)


def main():
    session = make_session()
    print(f"Watching Minecraft log: {LOG_PATH}")

    for line in follow_latest_log(LOG_PATH):

        # DEBUG (uncomment if needed)
        # print("LOG:", line)

        if m := JOIN_RE.search(line):
            player = m.group(1)
            msg = f"✅ **{player}** joined the server"
            print(msg)
            send_discord(session, msg)
            continue

        if m := LEAVE_RE.search(line):
            player = m.group(1)
            msg = f"❌ **{player}** left the server"
            print(msg)
            send_discord(session, msg)
            continue


if __name__ == "__main__":
    main()
