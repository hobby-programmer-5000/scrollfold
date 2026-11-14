**English** | [한국어](README.ko.md)

# Scrollfold

Split one wide image into up to 20 equal vertical strips for an X (Twitter) multi-image post, and preview how they line up before you post.

## Why I made this

X now allows 20 images per post, and people started posting one picture cut into 20 strips. Cutting by hand is tedious, and you can't see the result until it's posted.

## Features

- Strip count 1–20. **Auto** picks the count that best matches the image for the chosen strip ratio.
- **Strip ratio** presets measured from real X posts (see [reference.md](reference.md)): **1:2** (default, fills the biggest card), 9:16, 3:4, 1:1, **1:12** (thin slats) or Source.
- **If it doesn't fit**: Crop (keeps the center, status shows how much is kept) or Pad with a blurred copy, black or white. The picture is never stretched.
- Two scrollable panes: the source with red strip borders, and the strips laid out side by side with gaps. Zoom: Fit, 10–200%.
- **Optimize for X**: each strip becomes a JPEG with the long side ≤ 4096 px and ≤ 5 MB. Off: lossless PNG.
- Results go to `output/<input file name>/01.png …`. An existing folder is never overwritten (`name_2`, `name_3` …).
- "Open result folder" opens it in Explorer, Finder or your Linux file manager.
- Clear feedback: accepted formats are listed before you pick a file; each problem (unsupported, empty, too large, too narrow) gets its own message with how to fix it, shown inline. Saving shows "strip 3 of 20" and can be cancelled (Cancel or Esc); strips already written are kept.
- English / Korean UI. Starts in your system (OS or browser) language; switch with one click. Shortcuts: Ctrl+O open, Ctrl+S split & save, Ctrl+E open folder. Wheel scrolls vertically, Shift+wheel horizontally.

### Sample images

`samples/` has ready-made inputs grouped by format, shape (one per ratio preset) and tricky type (transparency, CMYK, 16-bit, EXIF-rotated, animated GIF, bad files). See [samples/README.md](samples/README.md).

### Supported formats

| Format | Desktop app | Local web mode (`server.py`) | Browser-only web |
|---|:-:|:-:|:-:|
| PNG, JPEG, WebP, GIF (first frame), BMP | ✓ | ✓ | ✓ |
| AVIF, ICO | ✓ | ✓ | ✓ (modern browsers) |
| TIFF, TGA, JPEG 2000, QOI, PPM, PCX | ✓ | ✓ (decoded by the server) | ✗ browsers can't read them |
| HEIC/HEIF (iPhone), RAW, PSD, SVG | ✗ | ✗ | ✗ — export to JPEG/PNG first |

All modes turn phone photos upright (EXIF orientation) and handle transparency; desktop and local mode also
handle CMYK and 16-bit images. Transparent areas become white in optimized (JPEG) output.

### Cautions

- **Do not use very large images.** An image is held uncompressed in memory (about 4 bytes per pixel)
  plus working copies: 100 MP ≈ 0.4 GB per copy. Downscale big scans first; X shows at most 4096 px per strip anyway.
- Animated GIF/WebP: only the first frame is used.
- Crop removes part of the picture; the status line shows how much is kept. Pad keeps everything.
- The image is never stretched.

### Large-image safeguards (and their limits)

| Safeguard | Desktop / local mode | Browser-only web |
|---|---|---|
| Warning above 100 MP | ✓ status line | ✓ status line |
| Refuse above 400 MP | ✓ checked from the file header **before** decoding | ✓ but only **after** the browser has decoded it |
| Preview size cap | 20,000 px long side | 16,000 px long side |
| Upload size cap for decoding (`/api/decode`) | 300 MB | — |
| Output size | ≤ 4096 px, ≤ 5 MB per strip with "Optimize for X" | same |

These reduce the risk; they do not remove it. Memory use also depends on your machine, other apps and the
browser. Images under 400 MP can still exhaust a small machine, and in browser-only mode the browser decodes
the file before Scrollfold can check it, so an oversized image can freeze or crash the tab.

**Use at your own risk.** Scrollfold is open-source software provided "as is" under the MIT License, without
warranty. If you open a very large image and the app, browser or system runs out of memory, slows down or
crashes, that is your responsibility. Save your other work first and keep images to a reasonable size.

Tip: 20 strips at 1:2 need a 10:1 panorama; at 1:12 about 5:3. Tall photos fit better as 1–4 strips.

## Three ways to use it

| Mode | How | Where results go |
|---|---|---|
| **Web, browser only** | Open `web/index.html` from any static host (e.g. GitHub Pages) | `.zip` download, or "Save to a folder…" in Chromium browsers |
| **Web, local** | `python server.py` → opens `http://127.0.0.1:8765/` | `output/<file name>/`, with "Open result folder" |
| **Desktop** | `python app.py` | `output/<file name>/` |

In both web modes the image is processed inside the browser and never uploaded. The local server listens on
127.0.0.1 only and accepts writes only from its own page (per-run token, Host check).

## Run from source (Windows, macOS, Linux)

No build needed. Make a virtual environment in the project folder, install Pillow into it, and run.
Nothing is installed system-wide. Needs Python 3.10+ with Tkinter (only for the desktop app).

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py        # desktop
.venv\Scripts\python server.py     # local web mode
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py            # desktop
.venv/bin/python server.py         # local web mode
```

- Linux: if `import tkinter` fails, install your distro's Tk package (for example `sudo apt install python3-tk`).
- macOS: the python.org installer includes Tk; with Homebrew Python you may need `brew install python-tk`.
- Browser-only mode needs no Python at all: serve the `web/` folder from any static host.

### Browser-only web: the minimum files

To host only the web version, copy these 7 files from `web/` and nothing else:
`index.html`, `app.css`, `app.js`, `split.js`, `i18n.js`, `icon.svg`, `icon.png`.
The test files (`*.test.mjs`, `selftest.*`) are not needed.

Opening `index.html` straight from disk (`file://`) does **not** work: browsers block ES modules there.
Serve the folder over HTTP: any static host (GitHub Pages, Netlify …), `python server.py`, or for a quick
look `python -m http.server -d web`.

## Optional: Windows exe

`build.bat` runs the tests and builds `dist\Scrollfold.exe` with PyInstaller. It is not required and not part of
regular testing; running from source is the supported way on every OS. The exe and the desktop window use
`icon.ico` / `web/icon.png`; rebuild both with `python tools/make_icon.py` after changing `web/icon.svg`.

## Project layout

```
app.py        desktop UI (Tkinter)
server.py     local web mode (standard library only)
core.py       splitting, X optimization, output folders (no GUI imports)
i18n.py       desktop UI strings (en, ko)
web/          web UI: index.html, app.css, app.js, split.js (logic), i18n.js, icon.svg, icon.png
samples/      sample inputs (CC0), see samples/README.md
test_*.py     Python tests: core, server, desktop UI, UI text
web/*.test.mjs  Node tests: web logic, UI text
web/selftest.html  web UI self-test in a browser (tools/web_selftest.py)
icon.ico      exe icon (made by tools/make_icon.py from the web/icon.svg design)
reference.md  references and their licenses
build.bat     all tests → build → smoke test (Windows)
tools/        smoke test, format matrix, sample and icon generators, self-test runner
```

## Contributors

- hobby-programmer-5000 — idea, requirements, testing on X
- Claude (Anthropic) — implementation, tests, documentation

## License

- Code: MIT ([LICENSE](LICENSE)).
- Sample images in `samples/`: CC0 1.0, public domain — see [samples/README.md](samples/README.md).
- Third-party licenses: [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
