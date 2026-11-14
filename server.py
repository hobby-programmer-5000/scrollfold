"""Scrollfold local web mode: serves web/ on 127.0.0.1 and saves strips into output/.

Usage: python server.py [--port 8765] [--no-browser]

Only this machine can connect (bound to 127.0.0.1). Writes need a per-run token that only
a page served by this server can read, so other websites cannot write files through it.
Standard library only; the browser does the image work.
"""
from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import re
import secrets
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import core

WEB_DIR = core.app_dir() / "web"
FILE_RE = re.compile(r"^\d{2,3}\.(png|jpg)$")
MAX_UPLOAD = 60 * 1024 * 1024
MAX_DECODE = 300 * 1024 * 1024  # source images sent for decoding (TIFF etc.)
MAX_STRIPS_PER_JOB = core.MAX_STRIPS
TYPES = {".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml",
         ".html": "text/html; charset=utf-8"}


class State:
    def __init__(self, out_base: Path):
        self.token = secrets.token_urlsafe(24)
        self.out_base = out_base
        self.jobs: dict[str, Path] = {}
        self.lock = threading.Lock()


def make_handler(state: State, port: int):
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        server_version = "Scrollfold"

        def log_message(self, fmt, *args):  # quiet
            pass

        # ------------------------------------------------ helpers
        def send(self, code: int, body: bytes = b"", ctype: str = "application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, obj, code=200):
            self.send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

        def host_ok(self) -> bool:
            # Blocks DNS-rebinding: the page must be addressed as localhost/127.0.0.1.
            return self.headers.get("Host", "") in allowed_hosts

        def write_ok(self) -> bool:
            return self.host_ok() and secrets.compare_digest(self.headers.get("X-Scrollfold-Token", ""), state.token)

        def body(self, limit: int = MAX_UPLOAD) -> bytes:
            n = int(self.headers.get("Content-Length") or 0)
            if n > limit:
                raise ValueError("upload too large")
            return self.rfile.read(n)

        # ------------------------------------------------ GET
        def do_GET(self):
            if not self.host_ok():
                return self.send(HTTPStatus.FORBIDDEN, b"bad host", "text/plain")
            path = self.path.split("?", 1)[0]
            if path == "/api/info":
                return self.send_json({"token": state.token, "output": str(state.out_base)})
            rel = "index.html" if path in ("/", "") else path.lstrip("/")
            target = (WEB_DIR / rel).resolve()
            if WEB_DIR.resolve() not in target.parents or not target.is_file():
                return self.send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")
            ctype = TYPES.get(target.suffix) or mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self.send(200, target.read_bytes(), ctype)

        # ------------------------------------------------ POST /api/jobs, POST /api/jobs/<id>/open
        def do_POST(self):
            if not self.write_ok():
                return self.send(HTTPStatus.FORBIDDEN, b"forbidden", "text/plain")
            parts = self.path.strip("/").split("/")
            try:
                if parts == ["api", "jobs"]:
                    name = core.safe_name(str(json.loads(self.body() or b"{}").get("name", "image")))
                    with state.lock:
                        folder = core.unique_dir(state.out_base, name)
                        folder.mkdir(parents=True)
                        job = secrets.token_hex(8)
                        state.jobs[job] = folder
                    return self.send_json({"id": job, "folder": str(folder)})
                if parts == ["api", "decode"]:
                    # Formats browsers can't read: decode with Pillow, return PNG. Nothing is stored.
                    try:
                        img = core.open_image(io.BytesIO(self.body(MAX_DECODE)))
                    except (core.SplitError, OSError) as err:
                        return self.send(HTTPStatus.UNPROCESSABLE_ENTITY, str(err).encode(), "text/plain")
                    buf = io.BytesIO()
                    img.save(buf, "PNG", compress_level=1)
                    return self.send(200, buf.getvalue(), "image/png")
                if len(parts) == 4 and parts[:2] == ["api", "jobs"] and parts[3] == "open":
                    folder = state.jobs.get(parts[2])
                    if not folder:
                        return self.send(HTTPStatus.NOT_FOUND, b"no such job", "text/plain")
                    core.open_in_file_manager(folder)
                    return self.send_json({"ok": True})
            except (ValueError, json.JSONDecodeError) as err:
                return self.send(HTTPStatus.BAD_REQUEST, str(err).encode(), "text/plain")
            self.send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")

        # ------------------------------------------------ PUT /api/jobs/<id>/<01.jpg>
        def do_PUT(self):
            if not self.write_ok():
                return self.send(HTTPStatus.FORBIDDEN, b"forbidden", "text/plain")
            parts = self.path.strip("/").split("/")
            if len(parts) != 4 or parts[:2] != ["api", "jobs"] or not FILE_RE.match(parts[3]):
                return self.send(HTTPStatus.BAD_REQUEST, b"bad path", "text/plain")
            folder = state.jobs.get(parts[2])
            if not folder:
                return self.send(HTTPStatus.NOT_FOUND, b"no such job", "text/plain")
            if len(list(folder.iterdir())) >= MAX_STRIPS_PER_JOB and not (folder / parts[3]).exists():
                return self.send(HTTPStatus.BAD_REQUEST, b"too many files", "text/plain")
            try:
                data = self.body()
            except ValueError as err:
                return self.send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, str(err).encode(), "text/plain")
            path = folder / parts[3]
            tmp = path.with_name(path.name + ".tmp")
            tmp.write_bytes(data)
            os.replace(tmp, path)
            self.send_json({"ok": True, "bytes": len(data)})

    return Handler


def serve(port: int, out_base: Path | None = None) -> ThreadingHTTPServer:
    """Start on 127.0.0.1:port (next free port if taken). Returns the running server."""
    state = State(out_base or core.output_root())
    for p in range(port, port + 20):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", p), make_handler(state, p))
            httpd.state = state
            return httpd
        except OSError:
            continue
    raise SystemExit(f"No free port in {port}-{port + 19}")


def main():
    ap = argparse.ArgumentParser(description="Scrollfold local web mode")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    httpd = serve(a.port)
    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    print(f"Scrollfold running at {url}  (Ctrl+C to stop)\nResults: {httpd.state.out_base}")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    sys.exit(main())
