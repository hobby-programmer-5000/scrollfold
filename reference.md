**English** | [한국어](reference.ko.md)

# References

What Scrollfold looked at while designing, and what each source's license lets us do.
Rule: we take **ideas** from these. We copy code or text only when the license allows it, and we credit it here.

## Everything taken from outside (index)

Every external thing this project uses or looked at, with its license. Details are in the sections below
and in THIRD-PARTY-NOTICES.md. Add a row here whenever something new comes in.

| What | Used how | License | Where it lives |
|---|---|---|---|
| Python + Tkinter (Tcl/Tk) | runtime | PSF; Tcl/Tk BSD-style | not in repo |
| Pillow | dependency (image decoding/encoding) | MIT-CMU | `requirements.txt`, not in repo |
| Aileron Regular font (dotcolon), bundled in Pillow | renders the corner labels in `samples/` images | CC0 | not in repo (inside Pillow) |
| PyInstaller | builds the optional Windows exe; its bootloader is inside the exe | GPL-2.0 + bootloader exception | not in repo (`build.bat`) |
| Node.js | runs the web tests (`web/*.test.mjs`) only | MIT | not in repo, not shipped |
| uv | creates the venv (dev tool) | MIT / Apache-2.0 | not in repo |
| UX guidelines: GOV.UK, Microsoft, Carbon, GNOME, NN/g (see "UX guidance" below) | ideas paraphrased, no text, code or assets copied | OGL v3 / CC BY 4.0 / © IBM / © GNOME authors / © NN/g | links below |
| Chrome Modern Web Guidance | design guidance followed, nothing copied | CC BY 4.0 (text) / Apache-2.0 (samples) | links below |
| Google Design, Interactive Canvas guidelines | general inspiration | © Google / CC BY 4.0 | links below |
| fotoner/strip-split, virtualbanana877/ImageSegmentation | idea only, code not read or copied | none (all rights reserved) | links below |
| 15 X posts | measured strip sizes/ratios, nothing downloaded or stored | © their authors | links below |
| X image limits (4096 px long side, 5 MB per photo, 20 per post) | optimization targets | facts, from measured posts and X's announcements | `core.py` |
| Qingming scroll (Qing court version, 1736) | first manual test only | public domain | not in repo |

Made by this project (not external): app code (MIT), the icon (`web/icon.svg`, drawn here; `web/icon.png` and `icon.ico` are drawn from the same shapes by `tools/make_icon.py`), and the sample images (CC0).

## Similar splitter sites

| Site | Repository | License | What we may use |
|---|---|---|---|
| Photo Strip Splitter (사진 세로 분할) — https://fotoner.github.io/strip-split/ | github.com/fotoner/strip-split (`index.html`, `og.png`) | **None** (no LICENSE file; GitHub API reports no license, checked 2026-11-14) | Idea only. Default copyright: do not copy code, text or images |
| ImageSegmentation — https://virtualbanana877.github.io/ImageSegmentation/ (URL inferred from repo name, page not opened) | github.com/virtualbanana877/ImageSegmentation (`index.html`) | **None** (same check) | Idea only. Do not copy |

We did not read either site's code, so Scrollfold is written independently.

## Design and web guidance

| Source | License (to confirm on the page footer) | How we use it |
|---|---|---|
| Chrome — Modern Web Guidance guides: https://developer.chrome.com/docs/modern-web-guidance/guides?hl=ko | Google developer docs are normally CC BY 4.0 for text and Apache-2.0 for code samples | Follow the guidance; if we copy a code sample, keep the Apache-2.0 notice and credit it here |
| Google Design: https://design.google/ | Articles are © Google, no reuse license | Inspiration only (it is an article index, not a spec) |
| Interactive Canvas design guidelines: https://developers.google.com/assistant/interactivecanvas/design?hl=ko | Same as Google developer docs above | General principles only (built for Assistant/smart displays) |

Not used: Google logos or product names as branding.

## Stock assets rule (icons, fonts, images, sounds)

- Only open-source assets that allow **commercial use**: e.g. MIT, Apache-2.0, OFL-1.1, CC0, CC BY.
  Not allowed: CC BY-NC / ND, "free for personal use", unclear or missing licenses.
- **Always credit** every asset: name, author, source URL, license — in THIRD-PARTY-NOTICES.md and in the app's
  About/credits view (desktop and web), even when the license (e.g. CC0) does not require it.
- Bundle assets locally with their license file; no hot-linking from CDNs at runtime.

### Points we take from them

- Follow the system light/dark scheme; theme scrollbars and form controls; respect high contrast and forced colors.
- Fluid sizes (rem, `clamp()`), Grid/Flexbox, container queries instead of fixed breakpoints; works from phone to desktop, portrait and landscape.
- Scroll panes show a fade or shadow only on sides with more content.
- Long file names truncate on one line.
- Same features by mouse, touch and keyboard; visible focus.
- Errors appear in one predictable place, only after the user acts.
- Heavy work (splitting, export) is broken into small tasks so the page stays responsive.
- Images are processed locally in the browser; file names are inserted as text (no `innerHTML`); a Content Security Policy is set.
- Keep the UI clean: few controls, critical controls not at the very bottom on small screens.

## UX guidance (checked 2026-11-14)

Only ideas are used, written in our own words; no text, code, icons or other assets are copied.
"License" is the license of each site's text, as checked on the page, footer or source repository.

| Source | License of the text | What we may do |
|---|---|---|
| GOV.UK Design System, File upload — https://design-system.service.gov.uk/components/file-upload/ | Open Government Licence v3.0, © Crown copyright (site footer) | reuse even text with attribution; we only use ideas |
| Microsoft, Design Windows apps — https://learn.microsoft.com/en-us/windows/apps/design/ | CC BY 4.0 (source repo MicrosoftDocs/windows-dev-docs, GitHub API: CC-BY-4.0) | reuse with attribution; ideas only here |
| IBM Carbon, File uploader usage — https://carbondesignsystem.com/components/file-uploader/usage/ | docs: "Copyright © 2026 IBM", no open license stated; Carbon *code* is Apache-2.0 | ideas only |
| GNOME HIG, Progress bars / Dialogs — https://developer.gnome.org/hig/patterns/feedback/progress-bars.html, https://developer.gnome.org/hig/patterns/feedback/dialogs.html | no license found (repo Teams/Websites/developer.gnome.org-hig has per-file attribution only, "© 2021 Allan Day") → treat as all rights reserved | ideas only |
| Nielsen Norman Group, 10 Usability Heuristics — https://www.nngroup.com/articles/ten-usability-heuristics/ | "Copyright © Jakob Nielsen", all rights reserved; citing with credit and link is allowed | ideas only, credited |
| Material Design 3, Progress indicators — https://m3.material.io/components/progress-indicators/guidelines | could not verify (page did not load without JavaScript) | not used |
| Apple Human Interface Guidelines | © Apple, all rights reserved; design resources only for Apple-platform mock-ups | not used |

### Ideas taken

- Show accepted formats and the size limit next to the drop zone, before a file is picked. (GOV.UK)
- One specific error per failure: wrong type (list types), too large (state limit), too narrow, empty or broken file. Say how to fix it. (GOV.UK, Carbon, NN/g #9)
- A real "Choose file" button next to drag and drop; drag and drop alone is not enough. (GOV.UK)
- Return focus to the button that opened the file dialog. Truncate long file names with the full name on hover. (Carbon)
- Progress with units ("strip 3 of 20") inline next to the work; offer Cancel for long work. (GNOME, NN/g #1 and #3)
- Prefer undo over confirmation dialogs; avoid error dialogs, show errors inline. (GNOME)
- One primary action per screen; let people re-split the same image with new settings without picking it again. (Carbon, GOV.UK)
- Keyboard shortcuts for frequent actions, shown in the UI. (NN/g #7, Microsoft)

## X posts studied (measured 2026-11-14)

Found with X search ("20 images", "20枚", min_faves) after X raised the limit to 20 images per post.
Strip sizes are the stored originals (`name=orig`); "shown" is the card size on desktop web (768 px window).
We looked at these to choose ratios only; none of their images are copied or stored.

| Post | Strips | Strip size | Ratio | Shown | Style |
|---|---|---|---|---|---|
| https://x.com/Crain1Art/status/2121009306233438440 | 20 | 272×4096 | 1:15 | 45×703 | thin slats, silhouette on red |
| https://x.com/torious_0/status/2121059712892571839 | 20 | 285×3840 | 1:13.5 | 51×703 | thin slats, illustration |
| https://x.com/ExploreFranceJP/status/2121078745440354653 | 20 | 220×2975 | 1:13.5 | 51×703 | thin slats, photo |
| https://x.com/Artistreccs/status/2121057006656393629 | 20 | 102×1152 | 1:11 | 61×703 | thin slats |
| https://x.com/miku_emori/status/2121095856665555156 | 20 | 113×1133 | 1:10 | 69×703 | thin slats |
| https://x.com/NousResearch/status/2121348238100062408 | 20 | 140×1198 | 1:8.6 | 81×703 | slats, dark photo |
| https://x.com/doganuraldesign/status/2120971278165414385 | 8 | 2048×4096 | 1:2 | 335×672 | "16K" swipe panorama |
| https://x.com/conspiracyslyr/status/2121248257896816768 | 20 | 881×1790 | 1:2.03 | 335×683 | swipe panorama (Apollo 17) |
| https://x.com/GoogleIndia/status/2121250042485129613 | 20 | 1005×1920 | 1:1.91 | 335×642 | swipe, logo |
| https://x.com/japan_nobunaga/status/2121268348780421426 | 20 | 675×1200 | 9:16 | 335×597 | swipe, "you'll see why" |
| https://x.com/ito_pro_illust/status/2121124737581830230 | ~20 | ~1536×2048 | 3:4 | 335×447 | separate illustrations (not a split) |
| https://x.com/HazoZOYAKU/status/2121117502340247653 | 8 | 240–1056 × 3200 | mixed | 51×703 | **uneven** strip widths, artistic |
| https://x.com/someki_noi/status/2121119561026253021 | 11 | 3300×2500 | 4:3 | 452×384 | flip-book frames (not a split) |
| https://x.com/Ayumu_japan_art/status/2121093853470159030, https://x.com/elle_piyo/status/2121175053056549308, https://x.com/hdrnssr/status/2121324659346125030 | — | mixed | mixed | — | galleries of separate images (not splits) |

### What the measurements say

- X keeps each image's own ratio. A card is at most about **335 px wide and ~700 px tall** (desktop web),
  with a **6 px gap** between cards.
- So **1:2** (≈335×670) is the largest card: thick strips you swipe through (Google India, Apollo 17, 16K post).
- **1:8–1:15** is the other popular look: thin slats, 45–80 px wide, 10+ visible at once like blinds.
- Popular uploads use the full **4096 px** long side (X's maximum); smaller strips look soft when opened.
- Ideas not built (yet): uneven strip widths (HazoZOYAKU), flip-book frame sequences (someki_noi).

→ Presets: Source (default, splits the image as is), 1:2, 9:16, 3:4, 1:1, 1:12.

## Sample image

- Along the River During the Qingming Festival (Qing court version, 1736) — Wikimedia Commons,
  https://commons.wikimedia.org/wiki/File:Along_the_River_7-119-3.jpg — public domain (artwork). Not stored in this repo.
