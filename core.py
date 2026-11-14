"""Scrollfold core logic: split an image into vertical strips and save them.

No GUI imports here, so it can be tested on its own.
"""
from __future__ import annotations

import io
import os
import re
import subprocess
import sys
from pathlib import Path

import warnings

from PIL import Image, ImageFilter, ImageOps

APP_NAME = "Scrollfold"
DEFAULT_STRIPS = 20
MIN_STRIPS = 1
MAX_STRIPS = 20          # X allows up to 20 images per post

# X post limits used by the "optimize for X" option.
X_MAX_SIDE = 4096         # longest side in pixels
X_MAX_BYTES = 5 * 1024 * 1024  # 5 MB per photo
JPEG_QUALITIES = (92, 88, 84, 80, 75, 70, 65, 60, 50, 40)

# Very wide scrolls and panoramas can exceed Pillow's default bomb guard (~89 MP).
# Allow up to 400 MP; anything larger is refused with a clear message.
Image.MAX_IMAGE_PIXELS = 400_000_000

OUTPUT_DIR_NAME = "output"


class SplitError(Exception):
    """A problem the user can fix. `kind` + `info` let the UI show a specific, translated message."""

    def __init__(self, message: str, kind: str = "other", **info):
        super().__init__(message)
        self.kind = kind
        self.info = info


class Cancelled(Exception):
    """Saving was cancelled; `saved` lists the files already written."""

    def __init__(self, saved: list):
        super().__init__(f"cancelled after {len(saved)} files")
        self.saved = saved


# Formats each mode can read (shown next to the file picker).
DESKTOP_FORMATS = "PNG, JPEG, WebP, AVIF, GIF, BMP, ICO, TIFF, TGA, JPEG 2000, QOI, PPM, PCX"


def describe_error(err: Exception) -> tuple[str, dict]:
    """(message key, values) for showing an error to the user. Keys live in i18n.py."""
    if isinstance(err, SplitError):
        return err.kind, err.info
    if isinstance(err, Image.UnidentifiedImageError):
        return "unsupported", {"formats": DESKTOP_FORMATS}
    if isinstance(err, MemoryError):
        return "out_of_memory", {}
    if isinstance(err, OSError):
        return "file_problem", {"detail": str(err)}
    return "other", {"detail": str(err)}


# ---------------------------------------------------------------- geometry

def strip_boxes(width: int, height: int, count: int) -> list[tuple[int, int, int, int]]:
    """Crop boxes for `count` equal-width strips.

    Every strip has the same width. Leftover pixels (width % count) are trimmed
    evenly from the left and right edges.
    """
    if not MIN_STRIPS <= count <= MAX_STRIPS:
        raise SplitError(f"count must be {MIN_STRIPS}-{MAX_STRIPS}", "bad_count", min=MIN_STRIPS, max=MAX_STRIPS)
    strip_w = width // count
    if strip_w < 1:
        raise SplitError(f"image is {width}px wide, too narrow for {count} strips", "too_narrow",
                         width=width, count=count, max=min(MAX_STRIPS, width))
    left0 = (width - strip_w * count) // 2
    return [(left0 + i * strip_w, 0, left0 + (i + 1) * strip_w, height) for i in range(count)]


def split_image(img: Image.Image, count: int) -> list[Image.Image]:
    return [img.crop(box) for box in strip_boxes(img.width, img.height, count)]


# ---------------------------------------------------------------- strip ratio

# Width:height of one strip, from measured X posts (see reference.md).
# X shows each image at its own ratio inside a card at most ~335 px wide and ~700 px tall (desktop),
# so 1:2 fills the card (largest strip in the feed); 1:12 gives the thin "slats" look.
# None keeps the source as it is.
RATIOS: dict[str, tuple[int, int] | None] = {
    "1:2": (1, 2),
    "9:16": (9, 16),
    "3:4": (3, 4),
    "1:1": (1, 1),
    "1:12": (1, 12),
    "original": None,
}
DEFAULT_RATIO = "1:2"
LARGE_WARN_PIXELS = 100_000_000   # warn above 100 MP: slow, lots of memory
FIT_MODES = ("crop", "blur", "black", "white")
DEFAULT_FIT = "crop"


def target_aspect(count: int, ratio: tuple[int, int]) -> float:
    """Width / height of the whole image once `count` strips of `ratio` sit side by side."""
    return count * ratio[0] / ratio[1]


def suggest_count(width: int, height: int, ratio: tuple[int, int] | None) -> int:
    """Strip count whose total shape is closest to the source (1-20)."""
    if ratio is None:
        return DEFAULT_STRIPS
    n = round((width / height) / (ratio[0] / ratio[1]))
    return min(MAX_STRIPS, max(MIN_STRIPS, n))


def crop_box(width: int, height: int, aspect: float) -> tuple[int, int, int, int]:
    """Largest centered box of the given aspect inside width x height."""
    if width / height > aspect:
        w = max(1, round(height * aspect))
        x = (width - w) // 2
        return (x, 0, x + w, height)
    h = max(1, round(width / aspect))
    y = (height - h) // 2
    return (0, y, width, y + h)


def pad_size(width: int, height: int, aspect: float) -> tuple[int, int]:
    """Smallest canvas of the given aspect that holds width x height."""
    if width / height > aspect:
        return width, max(height, round(width / aspect))
    return max(width, round(height * aspect)), height


def fit_image(img: Image.Image, count: int, ratio: tuple[int, int] | None, mode: str) -> Image.Image:
    """Reshape `img` so `count` strips of `ratio` cover it. Never stretches the picture.

    crop  - cut the centered part that fits.
    blur  - keep everything, fill the empty sides with a blurred, enlarged copy.
    black / white - keep everything, fill the empty sides with that color.
    """
    if ratio is None:
        return img
    aspect = target_aspect(count, ratio)
    if mode == "crop":
        return img.crop(crop_box(img.width, img.height, aspect))
    if mode not in FIT_MODES:
        raise SplitError(f"unknown fit mode: {mode}")
    cw, ch = pad_size(img.width, img.height, aspect)
    if (cw, ch) == img.size:
        return img
    src = _to_rgb(img)
    if mode == "blur":
        # Cover the canvas (scale up, center-crop), then blur hard and darken a little.
        s = max(cw / src.width, ch / src.height)
        bw, bh = max(cw, round(src.width * s)), max(ch, round(src.height * s))
        small = src.resize((max(1, bw // 8), max(1, bh // 8)), Image.BILINEAR)
        small = small.filter(ImageFilter.GaussianBlur(6)).point(lambda v: v * 3 // 4)
        bg = small.resize((bw, bh), Image.BILINEAR)
        x, y = (bw - cw) // 2, (bh - ch) // 2
        canvas = bg.crop((x, y, x + cw, y + ch))
    else:
        canvas = Image.new("RGB", (cw, ch), (0, 0, 0) if mode == "black" else (255, 255, 255))
    canvas.paste(src, ((cw - src.width) // 2, (ch - src.height) // 2))
    return canvas


# ---------------------------------------------------------------- X optimize

def fit_within(size: tuple[int, int], max_side: int) -> tuple[int, int]:
    w, h = size
    scale = min(1.0, max_side / max(w, h))
    return max(1, round(w * scale)), max(1, round(h * scale))


def _to_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg
    return img.convert("RGB")


def optimize_for_x(img: Image.Image) -> bytes:
    """JPEG bytes that fit X limits: longest side <= 4096 px and <= 5 MB."""
    img = _to_rgb(img)
    size = fit_within(img.size, X_MAX_SIDE)
    if size != img.size:
        img = img.resize(size, Image.LANCZOS)
    while True:
        # Binary search: best quality in the list that fits, in ~4 encodes.
        lo, hi, best = 0, len(JPEG_QUALITIES) - 1, None
        while lo <= hi:
            mid = (lo + hi) // 2
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=JPEG_QUALITIES[mid], optimize=True)
            if buf.tell() <= X_MAX_BYTES:
                best, hi = buf.getvalue(), mid - 1
            else:
                lo = mid + 1
        if best is not None:
            return best
        # Still too big at the lowest quality: shrink and retry.
        img = img.resize((max(1, img.width * 3 // 4), max(1, img.height * 3 // 4)), Image.LANCZOS)


# ---------------------------------------------------------------- loading

def prepare(img: Image.Image) -> Image.Image:
    """Normalize any opened image for splitting.

    - first frame only (animated GIF/WebP/APNG)
    - EXIF orientation applied, so phone photos are upright
    - converted to RGB, or RGBA when it has transparency (CMYK, 16-bit, palette, 1-bit, ...)
    """
    img.seek(0) if getattr(img, "is_animated", False) else None
    img = ImageOps.exif_transpose(img)
    has_alpha = img.mode in ("RGBA", "LA", "PA", "La", "RGBa") or (img.mode == "P" and "transparency" in img.info)
    if img.mode.startswith("I;16") or img.mode in ("I", "F"):
        # 16/32-bit: scale to 8-bit instead of clipping everything to white.
        lo, hi = img.getextrema() if img.mode != "I;16" else img.convert("I").getextrema()
        scale = 255 / max(1, hi - lo)
        img = img.convert("I").point(lambda v: (v - lo) * scale).convert("L")
    target = "RGBA" if has_alpha else "RGB"
    return img if img.mode == target else img.convert(target)


def open_image(path) -> Image.Image:
    """Open, fully load and normalize. Refuses images above MAX_IMAGE_PIXELS instead of only warning."""
    if isinstance(path, (str, Path)) and Path(path).is_file() and Path(path).stat().st_size == 0:
        raise SplitError("the file is empty", "empty")
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            with Image.open(path) as im:
                im.load()
                return prepare(im)
        except (Image.DecompressionBombWarning, Image.DecompressionBombError) as err:
            raise SplitError(f"image is too large (limit {Image.MAX_IMAGE_PIXELS // 1_000_000} MP)", "too_large",
                             limit=Image.MAX_IMAGE_PIXELS // 1_000_000) from err


# ---------------------------------------------------------------- output

def safe_name(stem: str) -> str:
    """Folder name that is valid on Windows, macOS and Linux."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", stem).strip(" .")
    if name.upper() in {"CON", "PRN", "AUX", "NUL"} or re.fullmatch(r"(?i)(COM|LPT)\d", name):
        name = "_" + name
    return name[:100] or "image"


def unique_dir(base: Path, name: str) -> Path:
    """base/name, or base/name_2, name_3 ... if it already exists. Never reuses a folder."""
    candidate = base / name
    n = 2
    while candidate.exists():
        candidate = base / f"{name}_{n}"
        n += 1
    return candidate


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def user_data_dir() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA") or Path.home())
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return root / APP_NAME


def output_root() -> Path:
    """`output/` next to the app; the per-user data folder if that is not writable."""
    preferred = app_dir() / OUTPUT_DIR_NAME
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        probe = preferred / ".write_test"
        probe.write_bytes(b"")
        probe.unlink()
        return preferred
    except OSError:
        alt = user_data_dir() / OUTPUT_DIR_NAME
        alt.mkdir(parents=True, exist_ok=True)
        return alt


def save_strips(strips: list[Image.Image], folder: Path, optimize: bool, progress=None, cancel=None) -> list[Path]:
    """Write strips as 01.png ... (or 01.jpg when optimized). Files are written via .tmp + replace.

    `cancel` is an optional threading.Event; when set, stops before the next strip and raises Cancelled.
    Strips already written are kept (nothing is deleted).
    """
    folder.mkdir(parents=True, exist_ok=False)
    digits = max(2, len(str(len(strips))))
    paths = []
    for i, strip in enumerate(strips, 1):
        if cancel is not None and cancel.is_set():
            if not paths:
                folder.rmdir()  # nothing written: don't leave an empty folder behind
            raise Cancelled(paths)
        ext = "jpg" if optimize else "png"
        path = folder / f"{i:0{digits}d}.{ext}"
        tmp = path.with_name(path.name + ".tmp")
        if optimize:
            tmp.write_bytes(optimize_for_x(strip))
        else:
            strip.save(tmp, "PNG")
        os.replace(tmp, path)
        paths.append(path)
        if progress:
            progress(i, len(strips))
    return paths


def split_file(src: Path, count: int, optimize: bool, out_base: Path | None = None, progress=None,
               ratio: tuple[int, int] | None = None, mode: str = DEFAULT_FIT, cancel=None) -> tuple[Path, list[Path]]:
    """Fit `src` to the strip ratio, split it and save into <out_base>/<file name>/. Returns (folder, files)."""
    img = open_image(src)
    strips = split_image(fit_image(img, count, ratio, mode), count)
    folder = unique_dir(out_base or output_root(), safe_name(Path(src).stem))
    return folder, save_strips(strips, folder, optimize, progress, cancel)


def open_in_file_manager(path: Path) -> None:
    """Open a folder in Explorer / Finder / the desktop's file manager."""
    path = Path(path)
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606 - opens a folder we created
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
