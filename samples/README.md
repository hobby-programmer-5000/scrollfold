**English** | [한국어](README.ko.md)

# Sample inputs

Try Scrollfold with these. Every image here is drawn by `tools/make_samples.py` (no photos or artwork from anyone else).
Run that script to recreate them, and `tools/split_samples.py <empty folder>` to split them all at once.

| Folder | What it is | Suggested settings |
|---|---|---|
| `by-format/` | The same 1500×300 scene as PNG, JPEG, WebP, AVIF, GIF, BMP, TIFF, TGA, JPEG 2000, QOI, PPM, PCX, ICO | any; TIFF/TGA/JP2/QOI/PPM/PCX need the desktop app or local web mode |
| `by-shape/panorama-10x1_for-1-2.jpg` | 4000×400 | 1:2, 20 strips — the big swipe cards |
| `by-shape/panorama-11x1_for-9-16.jpg` | 4000×356 | 9:16, 20 strips |
| `by-shape/panorama-15x1_for-3-4.jpg` | 4000×267 | 3:4, 20 strips |
| `by-shape/panorama-20x1_for-1-1.jpg` | 4000×200 | 1:1, 20 strips |
| `by-shape/wide-5x3_for-1-12-slats.jpg` | 2400×1440 | 1:12, 20 strips — thin slats |
| `by-shape/square-1x1.jpg`, `tall-3x4.jpg` | square and tall photo | 1:2 with "Pad: blur", 2 strips |
| `by-type/transparent-rounded.png` | rounded corners with transparency | transparent areas turn white in JPEG output |
| `by-type/cmyk.jpg` | CMYK JPEG | converted to RGB |
| `by-type/grayscale.png`, `grayscale-16bit.png` | 8-bit and 16-bit gray | 16-bit is scaled to 8-bit |
| `by-type/phone-photo-exif-rotated.jpg` | stored sideways with EXIF orientation 6 | comes out upright |
| `by-type/animated.gif` | 3 frames | only the first frame is used |
| `by-type/too-narrow-19px.png` | 19 px wide | refused with 20 strips (too narrow) |
| `by-type/not-an-image.png` | a text file named .png | refused |

## License: CC0 1.0 (public domain)

These images are not edited from any photo or artwork. `tools/make_samples.py` draws them from scratch
(gradients, shapes, random stars). The small corner labels use Aileron Regular, the default font bundled with
Pillow, which is itself CC0 (https://dotcolon.net/fonts/aileron).

To the extent possible under law, the authors waive all copyright in the images in this `samples/` folder
under CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/ — use them for anything, no credit needed.
(The scripts that make them are code and stay under the project's MIT License.)
