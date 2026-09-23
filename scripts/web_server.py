"""Yerel arayüz ve güncel kuzgun API'si. Yalnız 127.0.0.1 üzerinde dinler."""
import argparse
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

def latest(root=ROOT):
    files = sorted(p for p in (root / "kuzgunlar").glob("*.md")
                   if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem))
    if not files:
        return None
    p = files[-1]
    return {"tarih": p.stem, "metin": p.read_text(encoding="utf-8")}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web" / "dist"), **kwargs)

    def do_GET(self):
        if urlsplit(self.path).path == "/api/kuzgun":
            try:
                payload = json.dumps(latest(), ensure_ascii=False).encode()
                status = 200
            except (OSError, UnicodeError):
                payload = b'{"error":"Kuzgun okunamadi"}'
                status = 503
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()

    def list_directory(self, path):
        self.send_error(404)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print(f"Küçük Konsey: http://127.0.0.1:{args.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
