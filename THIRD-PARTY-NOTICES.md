**English** | [한국어](THIRD-PARTY-NOTICES.ko.md)

# Third-party notices

Scrollfold uses the following third-party software. A built executable bundles them.

| Component | License | Link |
|---|---|---|
| Python (incl. Tkinter, Tcl/Tk) | PSF License; Tcl/Tk: BSD-style | https://docs.python.org/3/license.html |
| Pillow | MIT-CMU | https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| PyInstaller bootloader (only in the optional Windows exe) | GPL-2.0 with the bootloader exception (allows distributing the built exe under any license) | https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt |

Pillow wheels also bundle libjpeg-turbo, libpng, zlib, libwebp, libtiff, FreeType and others under their own
permissive licenses; see Pillow's LICENSE file for the full list.

Sample images (`samples/`, CC0) contain small labels rendered with **Aileron Regular** (dotcolon, CC0),
the default font bundled with Pillow: https://dotcolon.net/fonts/aileron

The web UI (`web/`) uses no third-party code, fonts or icons. The icon (`web/icon.svg`, `web/icon.png`, `icon.ico`) is drawn for this project.
Design guidance (not copied content): Chrome Modern Web Guidance, CC BY 4.0 — see reference.md.
