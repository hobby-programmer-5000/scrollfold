"""Desktop UI flows, run without showing a window (Tk root is withdrawn).

Covers what was checked by hand before: errors shown inline (no pop-ups), language switch,
auto count, saving, cancelling with Esc, opening the result folder. Needs Tk (no display tricks on Windows/macOS;
on Linux CI use xvfb-run).
"""
import shutil
import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

import app
import core

SAMPLES = Path(__file__).parent / "samples"


class DesktopFlows(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "out"
        self.out.mkdir()
        self.patches = [mock.patch.object(core, "output_root", return_value=self.out),
                        mock.patch.object(core, "open_in_file_manager"),
                        mock.patch.object(app.messagebox, "showerror", side_effect=AssertionError("pop-up shown"))]
        self.opened = [p.start() for p in self.patches][1]
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = app.App(self.root)
        self.app.lang = "en"
        self.app.apply_lang()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.root.destroy()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def pump(self, until=lambda: True, timeout=60):
        end = time.time() + timeout
        while time.time() < end:
            self.root.update()
            if until():
                return
            time.sleep(0.01)
        self.fail("timed out")

    def error_text(self):
        self.assertEqual(self.app.l_status.cget("style"), "Error.TLabel", self.app.status.get())
        return self.app.status.get()

    # ---------------------------------------------------------- opening
    def test_not_an_image_inline_error(self):
        self.app.load(SAMPLES / "by-type" / "not-an-image.png")
        self.pump()
        self.assertIn("Supported:", self.error_text())
        self.assertIsNone(self.app.src)

    def test_empty_file(self):
        empty = self.tmp / "empty.png"
        empty.write_bytes(b"")
        self.app.load(empty)
        self.assertIn("empty", self.error_text())

    def test_too_narrow_suggests_fewer_strips(self):
        self.app.load(SAMPLES / "by-type" / "too-narrow-19px.png")
        self.app.ratio_box.current(list(core.RATIOS).index("original"))
        self.app.count.set(20)
        self.app.redraw()
        self.assertIn("19 strips or fewer", self.error_text())

    def test_error_stays_after_resize(self):
        self.app.load(SAMPLES / "by-type" / "not-an-image.png")
        self.app.redraw()  # what a window resize triggers
        self.assertIn("Supported:", self.error_text())

    # ---------------------------------------------------------- normal use
    def test_auto_count_and_korean(self):
        self.app.load(SAMPLES / "by-shape" / "panorama-10x1_for-1-2.jpg")
        self.assertEqual(self.app.count.get(), 20)  # 10:1 with 1:2 strips
        self.app.toggle_lang()
        self.assertIn("조각 20개", self.app.status.get())
        self.assertEqual(self.app.b_save.cget("text"), "분할하고 저장")

    def test_save_then_open_folder(self):
        self.app.load(SAMPLES / "by-shape" / "panorama-10x1_for-1-2.jpg")
        self.app.save()
        self.pump(lambda: not self.app.saving)
        files = list((self.out / "panorama-10x1_for-1-2").iterdir())
        self.assertEqual(len(files), 20)
        self.assertEqual(str(self.app.b_folder.cget("state")), "normal")
        self.app.open_folder()
        self.opened.assert_called_once_with(self.out / "panorama-10x1_for-1-2")

    def test_escape_cancels_and_leaves_no_empty_folder(self):
        self.app.load(SAMPLES / "by-shape" / "panorama-10x1_for-1-2.jpg")
        self.app.save()
        self.assertTrue(self.app.b_cancel.winfo_manager())  # Cancel button shown while saving
        self.app.cancel_save()  # same handler as Esc
        self.pump(lambda: not self.app.saving)
        self.assertIn("Cancelled", self.app.status.get())
        self.assertFalse(self.app.b_cancel.winfo_manager())
        leftovers = [p for p in self.out.iterdir() if not any(p.iterdir())]
        self.assertEqual(leftovers, [])

    def test_large_image_warning(self):
        with mock.patch.object(core, "LARGE_WARN_PIXELS", 1000):
            self.app.load(SAMPLES / "by-format" / "scene.png")
            self.assertIn("Large image", self.app.status.get())


class Language(unittest.TestCase):
    def test_system_language_is_en_or_ko(self):
        self.assertIn(app.system_language(), ("en", "ko"))

    def test_linux_env_detection(self):
        import os
        with mock.patch.object(app.sys, "platform", "linux"):
            with mock.patch.dict(os.environ, {"LC_ALL": "ko_KR.UTF-8"}):
                self.assertEqual(app.system_language(), "ko")
            with mock.patch.dict(os.environ, {"LC_ALL": "en_US.UTF-8"}):
                self.assertEqual(app.system_language(), "en")


if __name__ == "__main__":
    unittest.main(verbosity=1)
