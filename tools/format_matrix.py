"""Stress test core.split_file across formats, color modes, sizes, ratios and quality.

Usage: .venv/Scripts/python -X utf8 tools/format_matrix.py [--keep DIR] [--heavy]

Generates every fixture itself (nothing copyrighted), runs the real save path, and checks:
  * the expected number of files, all strips the same size
  * strip ratio matches the chosen ratio (crop/pad) or the source (original)
  * optimized strips are JPEG, long side <= 4096, <= 5 MB
  * lossless runs (PNG out) reproduce the source pixels exactly
  * EXIF-rotated photos come out upright
Prints one line per case and exits 1 if any case fails.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw  # noqa: E402

import core  # noqa: E402

R34 = core.RATIOS["3:4"]


def pattern(w: int, h: int) -> Image.Image:
    """Colorful, detailed RGB test image: gradient, grid, diagonal, circles."""
    x = Image.linear_gradient("L").resize((w, h))
    y = Image.linear_gradient("L").rotate(90).resize((w, h))
    img = Image.merge("RGB", (x, y, Image.new("L", (w, h), 128)))
    d = ImageDraw.Draw(img)
    step = max(4, min(w, h) // 8)
    for gx in range(0, w, step):
        d.line([(gx, 0), (gx, h)], fill=(255, 255, 255))
    for gy in range(0, h, step):
        d.line([(0, gy), (w, gy)], fill=(0, 0, 0))
    d.line([(0, 0), (w, h)], fill=(255, 0, 0), width=max(1, step // 6))
    r = max(2, min(w, h) // 4)
    d.ellipse((w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r), outline=(255, 255, 0), width=max(1, r // 10))
    return img


def noise(w: int, h: int) -> Image.Image:
    return Image.merge("RGB", [Image.effect_noise((w, h), 120) for _ in range(3)])


# (name, file name, builder -> path, kwargs for split_file, expect)
# expect: "ok", "error" (clean SplitError/OSError expected)
def build_cases(d: Path, heavy: bool):
    base = pattern(1600, 400)  # 4:1
    rgba = base.convert("RGBA")
    rgba.putalpha(Image.linear_gradient("L").rotate(90).resize(base.size))
    cases = []

    def add(name, fname, make, expect="ok", **kw):
        cases.append((name, d / fname, make, kw, expect))

    def saver(img, fmt=None, **opts):
        return lambda p: img.save(p, fmt, **opts)

    # ---- formats and color modes (3:4 crop, optimized = the default UI settings)
    add("PNG RGB", "rgb.png", saver(base))
    add("PNG RGBA (alpha)", "rgba.png", saver(rgba))
    add("PNG palette+transparency", "p.png", saver(base.convert("P", palette=Image.ADAPTIVE), transparency=0))
    add("PNG grayscale L", "l.png", saver(base.convert("L")))
    add("PNG gray+alpha LA", "la.png", saver(rgba.convert("LA")))
    add("PNG 1-bit", "bw.png", saver(base.convert("1")))
    add("PNG 16-bit gray", "i16.png", saver(base.convert("L").convert("I").point(lambda v: v * 257).convert("I;16")))
    add("JPEG RGB", "rgb.jpg", saver(base, quality=95))
    add("JPEG progressive", "prog.jpg", saver(base, quality=90, progressive=True))
    add("JPEG grayscale", "gray.jpg", saver(base.convert("L")))
    add("JPEG CMYK", "cmyk.jpg", saver(base.convert("CMYK")))
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 CW on display: stored 1600x400 shows as 400x1600
    add("JPEG EXIF rotated (orientation 6)", "rot.jpg", saver(base, exif=exif.tobytes()), expect="upright")
    add("WebP lossy", "lossy.webp", saver(base, quality=80))
    add("WebP lossless alpha", "alpha.webp", saver(rgba, lossless=True))
    add("AVIF", "img.avif", saver(base, quality=70))
    add("GIF static", "s.gif", saver(base.convert("P", palette=Image.ADAPTIVE)))
    frames = [base.convert("P", palette=Image.ADAPTIVE), base.rotate(180).convert("P", palette=Image.ADAPTIVE)]
    add("GIF animated (first frame used)", "anim.gif", lambda p: frames[0].save(p, save_all=True, append_images=frames[1:], duration=200))
    add("BMP", "img.bmp", saver(base))
    add("TIFF RGB LZW", "lzw.tif", saver(base, compression="tiff_lzw"))
    add("TIFF CMYK", "cmyk.tif", saver(base.convert("CMYK")))
    add("TIFF RGBA", "rgba.tiff", saver(rgba))
    add("TGA", "img.tga", saver(base))
    add("ICO (256px)", "img.ico", saver(base.resize((256, 64)), sizes=[(256, 64)]))
    add("JPEG 2000", "img.jp2", saver(base))
    add("QOI", "img.qoi", saver(base))
    add("PPM", "img.ppm", saver(base))
    add("PCX", "img.pcx", saver(base))
    add("Not an image (text)", "fake.png", lambda p: p.write_text("hello"), expect="error")

    # ---- lossless round trip: original ratio, PNG out, pixels must match
    add("Lossless PNG round trip", "lossless.png", saver(base), expect="exact", ratio=None, optimize=False)
    add("Lossless RGBA round trip", "lossless_rgba.png", saver(rgba), expect="exact", ratio=None, optimize=False)

    # ---- sizes
    add("1x1 with 1 strip", "1x1.png", saver(Image.new("RGB", (1, 1), "red")), count=1, ratio=None)
    add("19px wide, 20 strips (too narrow)", "narrow.png", saver(pattern(19, 500)), expect="error", count=20, ratio=None)
    add("20x20, 20 strips of 1px", "20.png", saver(pattern(20, 20)), count=20, ratio=None)
    add("Wide scroll 16000x494", "scroll.jpg", saver(pattern(16000, 494), quality=90))
    add("Tall photo 3000x4000", "tall.jpg", saver(pattern(3000, 4000), quality=90))

    # ---- ratios x fit modes on a tall and a very wide source
    for src_name, img in (("tall 900x1600", pattern(900, 1600)), ("pano 12000x400", pattern(12000, 400))):
        fn = src_name.split()[0] + ".png"
        if not (d / fn).exists():
            img.save(d / fn)
        for rk in ("1:2", "9:16", "3:4", "1:1", "1:12"):
            for mode in core.FIT_MODES:
                cases.append((f"{src_name} {rk} {mode}", d / fn, None,
                              {"ratio": core.RATIOS[rk], "mode": mode, "count": 4 if "tall" in src_name else 20}, "ok"))

    # ---- quality: incompressible noise forces the JPEG quality/size loop
    if heavy:
        add("Noise 24000x4000 (5 MB loop)", "noise.png", saver(noise(24000, 4000)), ratio=None)
        add("Huge 20000x8000 (160 MP)", "huge.jpg", saver(pattern(20000, 8000), quality=85))
        add("Over the pixel limit (25000x17000)", "bomb.png", saver(Image.new("1", (25000, 17000))), expect="error")
    else:
        add("Noise 12000x3000 (5 MB loop)", "noise.png", saver(noise(12000, 3000)), ratio=None)
    return cases


def expected_source(path: Path) -> Image.Image:
    with Image.open(path) as im:
        return core.prepare(im)


def check(name, path, kw, expect, out_base):
    count = kw.get("count", 20)
    ratio = kw.get("ratio", R34)
    mode = kw.get("mode", "crop")
    optimize = kw.get("optimize", True)
    try:
        folder, files = core.split_file(path, count, optimize, out_base, ratio=ratio, mode=mode)
    except Exception as err:  # noqa: BLE001
        if expect == "error":
            return True, f"refused cleanly: {type(err).__name__}: {str(err)[:70]}"
        return False, f"{type(err).__name__}: {err}"
    if expect == "error":
        return False, "expected a refusal but it saved files"
    if len(files) != count:
        return False, f"{len(files)} files, expected {count}"
    sizes = set()
    for f in files:
        with Image.open(f) as im:
            sizes.add(im.size)
            if optimize:
                if im.format != "JPEG" or max(im.size) > core.X_MAX_SIDE or f.stat().st_size > core.X_MAX_BYTES:
                    return False, f"{f.name}: {im.format} {im.size} {f.stat().st_size} B breaks X limits"
    if len(sizes) != 1:
        return False, f"strip sizes differ: {sorted(sizes)[:3]}"
    sw, sh = sizes.pop()
    src = expected_source(path)
    if ratio:
        want = ratio[0] / ratio[1]
        if abs(sw / sh - want) > max(0.02, 2 / sh + 2 / sw):
            return False, f"strip {sw}x{sh} is not {ratio[0]}:{ratio[1]}"
    note = f"{count} x {sw}x{sh}, max {max(f.stat().st_size for f in files) / 1e6:.2f} MB"
    if expect == "upright":
        if not src.height > src.width:
            return False, "EXIF orientation not applied (image still sideways)"
        note += ", upright"
    if expect == "exact":
        boxes = core.strip_boxes(src.width, src.height, count)
        for f, box in zip(files, boxes):
            with Image.open(f) as im:
                if im.convert(src.mode).tobytes() != src.crop(box).tobytes():
                    return False, f"{f.name} pixels differ from source"
        note += ", pixels exact"
    return True, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=Path, help="keep fixtures and output in this folder")
    ap.add_argument("--heavy", action="store_true", help="add very large images (uses ~2 GB RAM)")
    a = ap.parse_args()
    work = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix="scrollfold_matrix_"))
    fixtures, out = work / "fixtures", work / "out"
    fixtures.mkdir(parents=True, exist_ok=True)
    out.mkdir(exist_ok=True)
    fails = 0
    cases = build_cases(fixtures, a.heavy)
    for name, path, make, kw, expect in cases:
        t0 = time.perf_counter()
        try:
            if make and not path.exists():
                make(path)
            ok, note = check(name, path, kw, expect, out)
        except Exception:  # noqa: BLE001
            ok, note = False, traceback.format_exc(limit=2).strip().splitlines()[-1]
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name:<38} {time.perf_counter() - t0:5.1f}s  {note}")
    print(f"\n{len(cases) - fails}/{len(cases)} passed")
    if not a.keep:
        shutil.rmtree(work, ignore_errors=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
