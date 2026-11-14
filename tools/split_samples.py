"""Split every image in samples/ with fitting settings, into a folder you choose.

Usage: .venv/Scripts/python -X utf8 tools/split_samples.py OUT_DIR

Writes OUT_DIR/<group>/<sample name>/01.jpg ... and OUT_DIR/SUMMARY.md.
Kept out of the project's output/ folder on purpose so output/ only holds your own results.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import core  # noqa: E402

SAMPLES = Path(__file__).resolve().parents[1] / "samples"
SHAPE_RATIO = {"for-1-2": "1:2", "for-9-16": "9:16", "for-3-4": "3:4", "for-1-1": "1:1", "for-1-12": "1:12"}


def settings(path: Path) -> tuple[str, str]:
    """(ratio key, fit mode) for a sample."""
    for tag, key in sorted(SHAPE_RATIO.items(), key=lambda kv: -len(kv[0])):  # "for-1-12" before "for-1-1"
        if tag in path.stem:
            return key, "crop"
    if path.stem.startswith(("square", "tall")):
        return "1:2", "blur"  # pad instead of cropping most of the picture away
    return core.DEFAULT_RATIO, "crop"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    out = Path(sys.argv[1]).resolve()
    if out.exists() and any(out.iterdir()):
        print(f"{out} is not empty; choose a new or empty folder.")
        return 1
    rows = ["| Group | Sample | Ratio | Fit | Result |", "|---|---|---|---|---|"]
    for path in sorted(SAMPLES.rglob("*")):
        if not path.is_file():
            continue
        group = path.parent.name
        key, mode = settings(path)
        ratio = core.RATIOS[key]
        try:
            img = core.open_image(path)
            # "too-narrow" asks for 20 strips on purpose to show the refusal.
            n = 20 if "too-narrow" in path.stem else core.suggest_count(*img.size, ratio)
            folder, files = core.split_file(path, n, True, out / group, ratio=ratio, mode=mode)
            folder = folder.rename(folder.with_name(path.name.replace(".", "_")))
            from PIL import Image
            with Image.open(folder / files[0].name) as im:
                size = f"{im.width}x{im.height}"
            result = f"{n} strips of {size} → `{group}/{folder.name}/`"
        except Exception as err:  # noqa: BLE001 - samples include deliberately bad files
            result = f"refused: {err}"
        rows.append(f"| {group} | {path.name} | {key} | {mode} | {result} |")
        print(rows[-1])
    (out / "SUMMARY.md").write_text("# Scrollfold sample output\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
