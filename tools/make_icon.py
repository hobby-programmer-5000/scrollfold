"""Draw the app icon (same design as web/icon.svg) as PNG + ICO with Pillow.

Usage: .venv/Scripts/python -X utf8 tools/make_icon.py
Writes web/icon.png (256 px, browser fallback + desktop window icon) and icon.ico (exe icon).
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RED = (0xE8, 0x45, 0x2C)
# (x, width, radius, opacity) in the 32x32 SVG grid, bars from y=8 to y=24
BARS = ((5, 5, 1.5, 1.0), (11.5, 5, 1.5, 0.85), (18, 5, 1.5, 0.7), (24.5, 2.5, 1, 0.55))


def draw(size: int) -> Image.Image:
    k = 8  # supersample, then shrink for smooth edges
    s = size * k / 32
    img = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, size * k - 1, size * k - 1), radius=8 * s, fill=RED)
    for x, w, r, a in BARS:
        c = tuple(round(255 * a + v * (1 - a)) for v in RED)  # white at opacity a over red
        d.rounded_rectangle((x * s, 8 * s, (x + w) * s, 24 * s), radius=r * s, fill=c)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    big = draw(256)
    big.save(ROOT / "web" / "icon.png", optimize=True)
    big.save(ROOT / "icon.ico", sizes=[(n, n) for n in (16, 24, 32, 48, 64, 128, 256)])
    print("web/icon.png, icon.ico")


if __name__ == "__main__":
    main()
