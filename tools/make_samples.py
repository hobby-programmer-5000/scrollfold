"""Generate the sample input images in samples/ (all drawn by this script, free to use).

Usage: .venv/Scripts/python -X utf8 tools/make_samples.py

samples/
  by-format/   the same scene saved in every supported format (PNG, JPEG, WebP, AVIF, ...)
  by-shape/    shapes that suit each strip ratio preset (10:1 panorama for 1:2, 5:3 for 1:12 slats, ...)
  by-type/     tricky inputs: transparency, CMYK, 16-bit, EXIF-rotated phone photo, animated GIF, grayscale
Files are kept small (long side <= 4000 px) so the repository stays light.
"""
from __future__ import annotations

import math
import random
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1] / "samples"


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def scene(w: int, h: int, seed: int = 7, palette: str = "dusk") -> Image.Image:
    """A layered landscape: sky gradient, sun, stars, mountain ridges, water. Reads well when cut into strips."""
    rnd = random.Random(seed)
    skies = {
        "dusk": [(18, 22, 58), (120, 52, 110), (244, 120, 74), (255, 196, 120)],
        "dawn": [(40, 70, 130), (140, 170, 210), (250, 210, 170), (255, 236, 200)],
        "night": [(4, 6, 20), (16, 22, 60), (40, 50, 110), (70, 80, 140)],
    }[palette]
    img = Image.new("RGB", (w, h))
    px = img.load()
    horizon = int(h * 0.62)
    for y in range(h):
        t = min(1, y / horizon)
        seg = min(len(skies) - 2, int(t * (len(skies) - 1)))
        c = lerp(skies[seg], skies[seg + 1], t * (len(skies) - 1) - seg)
        for x in range(w):
            px[x, y] = c
    d = ImageDraw.Draw(img)
    for _ in range(int(w * h / 3000)):  # stars in the upper sky
        x, y = rnd.randrange(w), rnd.randrange(int(h * 0.35))
        b = rnd.randint(140, 255)
        d.point((x, y), fill=(b, b, b))
    sun_x, sun_r = int(w * 0.62), max(8, int(h * 0.11))
    glow = Image.new("L", (w, h))
    ImageDraw.Draw(glow).ellipse((sun_x - sun_r * 3, horizon - sun_r * 4, sun_x + sun_r * 3, horizon + sun_r * 2), fill=110)
    img.paste((255, 214, 150), mask=glow.filter(ImageFilter.GaussianBlur(sun_r)))
    d.ellipse((sun_x - sun_r, horizon - sun_r * 2, sun_x + sun_r, horizon), fill=(255, 236, 196))
    ridges = [((60, 40, 80), 0.30, 0.020), ((40, 26, 60), 0.20, 0.035), ((22, 14, 36), 0.12, 0.06)]
    for color, amp, freq in ridges:
        phase = rnd.random() * 10
        pts = [(0, h)]
        for x in range(0, w + 8, 8):
            y = horizon - amp * h * (0.5 + 0.5 * math.sin(x * freq * 40 / w + phase)) * (0.6 + 0.4 * math.sin(x * 7.3 / w + phase * 2))
            pts.append((x, y))
        pts.append((w, h))
        d.polygon(pts, fill=color)
    water = Image.new("RGB", (w, h - horizon), (14, 10, 30))
    reflect = img.crop((0, horizon - (h - horizon), w, horizon)).transpose(Image.FLIP_TOP_BOTTOM)
    img.paste(Image.blend(reflect, water, 0.55), (0, horizon))
    for y in range(horizon + 4, h, max(3, h // 60)):  # ripples
        d.line([(0, y), (w, y)], fill=(70, 56, 90) if y < horizon + h // 12 else (30, 24, 60), width=1)
    return img


def badge(img: Image.Image, text: str) -> Image.Image:
    """Small label in the corner so people can tell samples apart."""
    d = ImageDraw.Draw(img)
    s = max(10, img.height // 30)
    d.rectangle((s, s, s + len(text) * s * 0.62 + s, s * 2.6), fill=(0, 0, 0))
    d.text((s * 1.5, s * 1.2), text, fill=(255, 255, 255), font_size=s)
    return img


def save(img: Image.Image, path: Path, **kw):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, **kw)
    print(f"{path.relative_to(ROOT.parent)}  {img.size[0]}x{img.size[1]}  {path.stat().st_size / 1024:.0f} KB")


def main() -> int:
    for sub in ("by-format", "by-shape", "by-type"):  # regenerate images only; keep README files
        shutil.rmtree(ROOT / sub, ignore_errors=True)
    # ---- by-format: one 1500x300 (5:1) scene in every format (small: BMP/PPM are uncompressed)
    base = badge(scene(1500, 300, 1, "dusk"), "by-format")
    f = ROOT / "by-format"
    rgba = base.convert("RGBA")
    save(base, f / "scene.png", optimize=True)
    save(base, f / "scene.jpg", quality=90)
    save(base, f / "scene.webp", quality=88)
    save(base, f / "scene.avif", quality=70)
    save(base.convert("P", palette=Image.ADAPTIVE, colors=255), f / "scene.gif")
    save(base, f / "scene.bmp")
    save(base, f / "scene.tif", compression="tiff_lzw")
    save(base, f / "scene.tga", compression="tga_rle")
    save(base, f / "scene.jp2", quality_mode="dB", quality_layers=[38])
    save(base, f / "scene.qoi")
    save(base, f / "scene.ppm")
    save(base, f / "scene.pcx")
    save(rgba.resize((256, 51)), f / "scene.ico", sizes=[(256, 51)])

    # ---- by-shape: sizes that match each preset with 20 strips (or a few for tall/square)
    s = ROOT / "by-shape"
    save(badge(scene(4000, 400, 2, "dusk"), "10:1 -> 20 x 1:2"), s / "panorama-10x1_for-1-2.jpg", quality=90)
    save(badge(scene(4000, 356, 3, "dawn"), "11.25:1 -> 20 x 9:16"), s / "panorama-11x1_for-9-16.jpg", quality=90)
    save(badge(scene(4000, 267, 4, "night"), "15:1 -> 20 x 3:4"), s / "panorama-15x1_for-3-4.jpg", quality=90)
    save(badge(scene(4000, 200, 5, "dusk"), "20:1 -> 20 x 1:1"), s / "panorama-20x1_for-1-1.jpg", quality=90)
    save(badge(scene(2400, 1440, 6, "night"), "5:3 -> 20 x 1:12 slats"), s / "wide-5x3_for-1-12-slats.jpg", quality=90)
    save(badge(scene(1600, 1600, 7, "dawn"), "1:1 square"), s / "square-1x1.jpg", quality=90)
    save(badge(scene(1200, 1600, 8, "dusk"), "3:4 tall photo"), s / "tall-3x4.jpg", quality=90)

    # ---- by-type: tricky inputs
    t = ROOT / "by-type"
    sc = badge(scene(2400, 600, 9, "dawn"), "by-type")
    alpha = sc.convert("RGBA")
    mask = Image.new("L", sc.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((60, 60, sc.width - 60, sc.height - 60), radius=120, fill=255)
    alpha.putalpha(mask)
    save(alpha, t / "transparent-rounded.png", optimize=True)
    save(sc.convert("CMYK"), t / "cmyk.jpg", quality=90)
    save(sc.convert("L"), t / "grayscale.png", optimize=True)
    g16 = sc.convert("L").convert("I").point(lambda v: v * 257).convert("I;16")
    save(g16, t / "grayscale-16bit.png")
    exif = Image.Exif()
    exif[0x0112] = 6  # stored sideways, shown upright: a typical phone photo
    save(sc.rotate(90, expand=True), t / "phone-photo-exif-rotated.jpg", quality=90, exif=exif.tobytes())
    frames = [badge(scene(1600, 400, 10 + i, p), f"frame {i + 1} (only this one is used)" if i == 0 else f"frame {i + 1}")
              .convert("P", palette=Image.ADAPTIVE) for i, p in enumerate(("dusk", "night", "dawn"))]
    path = t / "animated.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=600, loop=0)
    print(f"{path.relative_to(ROOT.parent)}  1600x400 x3 frames  {path.stat().st_size / 1024:.0f} KB")
    save(Image.new("RGB", (19, 400), (200, 60, 60)), t / "too-narrow-19px.png")  # must be refused for 20 strips
    (t / "not-an-image.png").write_text("This file is text, not an image. Scrollfold should refuse it.\n")
    print("samples/by-type/not-an-image.png  (text)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
