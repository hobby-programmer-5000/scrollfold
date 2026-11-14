"""Open the web UI self-test in your browser, in local server mode, with a throw-away output folder.

Usage: .venv/Scripts/python -X utf8 tools/web_selftest.py [--static]

  (default)  serves web/ through server.py; results of the cancel test go to a temp folder, not output/
  --static   serves web/ as plain files (browser-only mode, like GitHub Pages)

The page title turns into "PASS n/n" or "FAIL k/n"; details are listed on the page. Ctrl+C to stop.
"""
from __future__ import annotations

import functools
import http.server
import shutil
import sys
import tempfile
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


def main() -> int:
    static = "--static" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="scrollfold_selftest_"))
    if static:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(server.WEB_DIR))
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    else:
        httpd = server.serve(8790, tmp)
    url = f"http://127.0.0.1:{httpd.server_address[1]}/selftest.html"
    print(f"Self-test: {url}\n(mode: {'browser-only' if static else 'local server'}; temp output: {tmp})")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
