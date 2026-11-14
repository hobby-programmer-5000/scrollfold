import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import server


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.httpd = server.serve(18765, Path(cls.tmp.name))
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.tmp.cleanup()

    def req(self, method, path, body=None, token=True, host=None):
        r = urllib.request.Request(self.base + path, data=body, method=method)
        if token:
            r.add_header("X-Scrollfold-Token", self.httpd.state.token)
        if host:
            r.add_header("Host", host)
        try:
            with urllib.request.urlopen(r) as res:
                return res.status, res.read()
        except urllib.error.HTTPError as e:
            with e:
                return e.code, e.read()

    def test_serves_page_and_info(self):
        code, body = self.req("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(b"Scrollfold", body)
        code, body = self.req("GET", "/api/info")
        self.assertEqual(json.loads(body)["token"], self.httpd.state.token)

    def test_save_flow_and_no_overwrite(self):
        folders = []
        for _ in range(2):
            code, body = self.req("POST", "/api/jobs", json.dumps({"name": "scroll"}).encode())
            self.assertEqual(code, 200)
            job = json.loads(body)
            folders.append(Path(job["folder"]).name)
            self.assertEqual(self.req("PUT", f"/api/jobs/{job['id']}/01.jpg", b"abc")[0], 200)
        self.assertEqual(folders, ["scroll", "scroll_2"])
        self.assertEqual((Path(self.tmp.name) / "scroll" / "01.jpg").read_bytes(), b"abc")

    def test_rejects_without_token_bad_host_or_bad_name(self):
        self.assertEqual(self.req("POST", "/api/jobs", b"{}", token=False)[0], 403)
        self.assertEqual(self.req("GET", "/api/info", host="evil.example:80")[0], 403)
        job = json.loads(self.req("POST", "/api/jobs", b'{"name":"x"}')[1])
        for bad in ("..%2Fescape.jpg", "a.exe", "01.jpg.tmp"):
            self.assertEqual(self.req("PUT", f"/api/jobs/{job['id']}/{bad}", b"z")[0], 400)

    def test_decode_tiff_for_browser(self):
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("CMYK", (40, 10), (0, 255, 0, 0)).save(buf, "TIFF")
        code, body = self.req("POST", "/api/decode", buf.getvalue())
        self.assertEqual(code, 200)
        with Image.open(io.BytesIO(body)) as im:
            self.assertEqual((im.format, im.size, im.mode), ("PNG", (40, 10), "RGB"))
        self.assertEqual(self.req("POST", "/api/decode", b"not an image")[0], 422)
        self.assertEqual(self.req("POST", "/api/decode", b"x", token=False)[0], 403)

    def test_open_folder_api(self):
        from unittest import mock
        job = json.loads(self.req("POST", "/api/jobs", b'{"name":"opened"}')[1])
        with mock.patch.object(server.core, "open_in_file_manager") as opened:
            self.assertEqual(self.req("POST", f"/api/jobs/{job['id']}/open")[0], 200)
            opened.assert_called_once_with(Path(job["folder"]))
            self.assertEqual(self.req("POST", "/api/jobs/nope/open")[0], 404)
            self.assertEqual(self.req("POST", f"/api/jobs/{job['id']}/open", token=False)[0], 403)
            self.assertEqual(opened.call_count, 1)

    def test_path_traversal_blocked(self):
        self.assertEqual(self.req("GET", "/../core.py")[0], 404)
        self.assertEqual(self.req("GET", "/%2e%2e/core.py")[0], 404)


if __name__ == "__main__":
    unittest.main(verbosity=1)
