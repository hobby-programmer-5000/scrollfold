import tempfile
import unittest
from pathlib import Path

from PIL import Image

import core


class StripBoxes(unittest.TestCase):
    def test_equal_widths_and_centered_trim(self):
        boxes = core.strip_boxes(2003, 100, 20)
        self.assertEqual(len(boxes), 20)
        self.assertEqual({b[2] - b[0] for b in boxes}, {100})
        self.assertEqual(boxes[0][0], 1)          # 3 leftover px: 1 left, 2 right
        self.assertEqual(boxes[-1][2], 2001)

    def test_strips_are_contiguous(self):
        boxes = core.strip_boxes(1000, 10, 7)
        for a, b in zip(boxes, boxes[1:]):
            self.assertEqual(a[2], b[0])

    def test_count_limits(self):
        for bad in (0, 21):
            with self.assertRaises(core.SplitError):
                core.strip_boxes(1000, 10, bad)

    def test_too_narrow(self):
        with self.assertRaises(core.SplitError):
            core.strip_boxes(10, 10, 20)


class Fit(unittest.TestCase):
    def test_suggest_count(self):
        self.assertEqual(core.suggest_count(16000, 494, (3, 4)), 20)   # very wide scroll caps at 20
        self.assertEqual(core.suggest_count(1500, 400, (3, 4)), 5)
        self.assertEqual(core.suggest_count(900, 1600, (3, 4)), 1)     # tall photo
        self.assertEqual(core.suggest_count(900, 1600, None), core.DEFAULT_STRIPS)

    def test_crop_gives_exact_strip_ratio(self):
        img = Image.new("RGB", (16000, 494))
        for n in (20, 7):
            strips = core.split_image(core.fit_image(img, n, (3, 4), "crop"), n)
            for s in strips:
                self.assertAlmostEqual(s.width / s.height, 3 / 4, delta=0.01)

    def test_crop_tall_cuts_top_and_bottom(self):
        out = core.fit_image(Image.new("RGB", (900, 1600)), 2, (3, 4), "crop")
        self.assertEqual(out.width, 900)
        self.assertEqual(out.height, 600)

    def test_pad_keeps_every_pixel_unstretched(self):
        src = Image.effect_noise((900, 1600), 50).convert("RGB")
        for mode in ("blur", "black", "white"):
            out = core.fit_image(src, 4, (3, 4), mode)
            self.assertAlmostEqual(out.width / out.height, 3.0, delta=0.01)
            x = (out.width - 900) // 2
            self.assertEqual(out.crop((x, 0, x + 900, 1600)).tobytes(), src.tobytes())

    def test_presets_match_web(self):
        import re
        js = (Path(__file__).parent / "web" / "split.js").read_text(encoding="utf-8")
        line = re.search(r"export const RATIOS = \{(.*?)\};", js).group(1)
        web = dict(re.findall(r'"?([\w:]+)"?: (\[\d+, \d+\]|null)', line))
        py = {k: ("null" if v is None else f"[{v[0]}, {v[1]}]") for k, v in core.RATIOS.items()}
        self.assertEqual(web, py)
        self.assertIn(f'DEFAULT_RATIO = "{core.DEFAULT_RATIO}"', js)

    def test_original_ratio_is_untouched(self):
        img = Image.new("RGB", (123, 45))
        self.assertIs(core.fit_image(img, 20, None, "crop"), img)


class Loading(unittest.TestCase):
    """Regressions found by tools/format_matrix.py."""

    def _roundtrip(self, img, fmt, **kw):
        import io
        buf = io.BytesIO()
        img.save(buf, fmt, **kw)
        buf.seek(0)
        return core.open_image(buf)

    def test_exif_rotation_applied(self):
        exif = Image.Exif()
        exif[0x0112] = 6
        out = self._roundtrip(Image.new("RGB", (160, 40)), "JPEG", exif=exif.tobytes())
        self.assertEqual(out.size, (40, 160))

    def test_modes_normalized(self):
        cases = [("CMYK", "JPEG", "RGB"), ("CMYK", "TIFF", "RGB"), ("L", "PNG", "RGB"), ("1", "PNG", "RGB"),
                 ("LA", "PNG", "RGBA"), ("RGBA", "WEBP", "RGBA")]
        for mode, fmt, want in cases:
            with self.subTest(mode=mode, fmt=fmt):
                self.assertEqual(self._roundtrip(Image.new(mode, (20, 10)), fmt).mode, want)

    def test_16bit_is_scaled_not_white(self):
        g = Image.linear_gradient("L").resize((64, 8)).convert("I").point(lambda v: v * 257).convert("I;16")
        out = self._roundtrip(g, "PNG")
        lo, hi = out.convert("L").getextrema()
        self.assertLess(lo, 10)
        self.assertGreater(hi, 245)

    def test_animated_gif_uses_first_frame(self):
        frames = [Image.new("P", (10, 10), 1), Image.new("P", (10, 10), 2)]
        import io
        buf = io.BytesIO()
        frames[0].save(buf, "GIF", save_all=True, append_images=frames[1:])
        buf.seek(0)
        self.assertEqual(core.open_image(buf).size, (10, 10))

    def test_pixel_limit_refused(self):
        with self.assertRaises(core.SplitError):
            self._roundtrip(Image.new("1", (25000, 17000)), "PNG")

    def test_not_an_image(self):
        import io
        with self.assertRaises(OSError):
            core.open_image(io.BytesIO(b"hello"))


class Ux(unittest.TestCase):
    def test_cancel_keeps_written_files(self):
        import threading
        ev = threading.Event()
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.png"
            Image.new("RGB", (400, 100)).save(src)
            def progress(i, n):
                if i == 3:
                    ev.set()
            with self.assertRaises(core.Cancelled) as cm:
                core.split_file(src, 10, False, Path(d) / "out", progress=progress, cancel=ev)
            self.assertEqual(len(cm.exception.saved), 3)
            self.assertEqual(len(list((Path(d) / "out" / "a").iterdir())), 3)
            ev.set()
            with self.assertRaises(core.Cancelled):
                core.split_file(src, 10, False, Path(d) / "out", cancel=ev)
            self.assertFalse((Path(d) / "out" / "a_2").exists())  # no empty folder left

    def test_errors_have_kinds(self):
        import io
        with tempfile.TemporaryDirectory() as d:
            empty = Path(d) / "e.png"
            empty.write_bytes(b"")
            for path, kind in ((empty, "empty"), (io.BytesIO(b"text"), "unsupported")):
                with self.assertRaises(Exception) as cm:
                    core.open_image(path)
                self.assertEqual(core.describe_error(cm.exception)[0], kind)
        with self.assertRaises(core.SplitError) as cm:
            core.strip_boxes(10, 10, 20)
        self.assertEqual((cm.exception.kind, cm.exception.info["max"]), ("too_narrow", 10))


class Optimize(unittest.TestCase):
    def test_large_strip_fits_x_limits(self):
        # Noise compresses badly, so this exercises the quality/size loop.
        img = Image.effect_noise((3000, 9000), 100).convert("RGB")
        data = core.optimize_for_x(img)
        self.assertLessEqual(len(data), core.X_MAX_BYTES)
        with Image.open(__import__("io").BytesIO(data)) as out:
            self.assertLessEqual(max(out.size), core.X_MAX_SIDE)
            self.assertEqual(out.format, "JPEG")

    def test_small_image_keeps_size(self):
        img = Image.new("RGBA", (100, 50), (255, 0, 0, 128))
        with Image.open(__import__("io").BytesIO(core.optimize_for_x(img))) as out:
            self.assertEqual(out.size, (100, 50))


class Output(unittest.TestCase):
    def test_never_overwrites_existing_folder(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "scroll.png"
            Image.new("RGB", (400, 100), "red").save(src)
            out = Path(d) / "out"
            f1, files1 = core.split_file(src, 20, False, out)
            f2, files2 = core.split_file(src, 20, True, out)
            self.assertEqual(f1.name, "scroll")
            self.assertEqual(f2.name, "scroll_2")
            self.assertEqual([p.name for p in files1][:2], ["01.png", "02.png"])
            self.assertEqual(files2[-1].name, "20.jpg")
            self.assertEqual(len(list(f1.iterdir())), 20)   # no .tmp left behind

    def test_safe_name(self):
        self.assertEqual(core.safe_name('a:b*c?'), "a_b_c_")
        self.assertEqual(core.safe_name("CON"), "_CON")
        self.assertEqual(core.safe_name(" . "), "image")
        self.assertEqual(core.safe_name("그림"), "그림")


if __name__ == "__main__":
    unittest.main(verbosity=1)
