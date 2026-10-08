#!/usr/bin/env python3
"""
Local host for the hangul drill.

Serves index.html and keeps your counts in progress.json, in this same folder.
Standard library only — no pip install, no venv.

    python server.py

Then leave it running and use the browser tab it opens.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import shutil
import sys
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "progress.json"
BACKUP = ROOT / "progress.bak.json"
TMP = ROOT / "progress.tmp.json"

FIRST_PORT = 8775   # the hiragana drill uses 8765, so both can run at once
PORT_TRIES = 20

_lock = threading.Lock()


def read_progress():
    """Load progress.json, falling back to the backup if the main file is damaged."""
    for path in (DATA, BACKUP):
        if not path.exists():
            continue
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as err:
            print(f"  ! {path.name} unreadable ({err}); trying backup", file=sys.stderr)
    return {}


def write_progress(data):
    """Write atomically so a crash mid-save can't leave a half-written file."""
    with _lock:
        TMP.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        if DATA.exists():
            shutil.copy2(DATA, BACKUP)
        os.replace(TMP, DATA)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    # --- helpers ---------------------------------------------------------
    def send_json(self, payload, code=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def is_api(self):
        return self.path.split("?")[0].rstrip("/") == "/api/progress"

    # --- routes ----------------------------------------------------------
    def do_GET(self):
        if self.is_api():
            return self.send_json(read_progress())
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if not self.is_api():
            return self.send_error(404)
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > 2_000_000:
            return self.send_json({"error": "bad length"}, 400)
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.send_json({"error": "bad json"}, 400)
        if not isinstance(data, dict) or "counts" not in data:
            return self.send_json({"error": "expected an object with counts"}, 400)
        try:
            write_progress(data)
        except OSError as err:
            print(f"  ! save failed: {err}", file=sys.stderr)
            return self.send_json({"error": "write failed"}, 500)
        retired = sum(1 for v in data["counts"].values() if v >= 10)
        print(f"  saved · {retired} retired", flush=True)
        return self.send_json({"saved": True})

    def end_headers(self):
        if self.path.endswith(".html") or self.path in ("/", ""):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # the save lines above are the only log worth reading


def main():
    if not (ROOT / "index.html").exists():
        sys.exit("index.html is missing — keep it in the same folder as server.py")

    server = None
    for port in range(FIRST_PORT, FIRST_PORT + PORT_TRIES):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"no free port between {FIRST_PORT} and {FIRST_PORT + PORT_TRIES}")

    url = f"http://127.0.0.1:{server.server_port}/"
    existing = read_progress().get("counts", {})
    retired = sum(1 for v in existing.values() if v >= 10)

    print(f"한글 연습장  {url}")
    print(f"progress.json  {DATA}")
    print(f"loaded         {len(existing)} characters seen · {retired} retired")
    print("Ctrl+C to stop.\n")

    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
