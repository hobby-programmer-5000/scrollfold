"""Scrollfold UI (Tkinter). Logic lives in core.py."""
from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageTk

import core
from i18n import t

GAP = 6                      # px between strips in the preview
PREVIEW_BG = "#15181c"
LINE_COLOR = (255, 64, 64)
ZOOMS = ("fit", "10%", "25%", "50%", "100%", "200%")
MAX_VIEW_SIDE = 20000        # cap for the rendered preview so huge images stay responsive


LIGHT = {"bg": "#f6f5f3", "surface": "#ffffff", "surface2": "#efeeeb", "ink": "#1d1c1a", "muted": "#6b6862",
         "line": "#dddad4", "accent": "#e8452c", "accent_hover": "#f05a42", "stage": "#1a1c20"}
DARK = {"bg": "#111214", "surface": "#1b1d20", "surface2": "#24272b", "ink": "#ecebe8", "muted": "#a09d97",
        "line": "#2f3236", "accent": "#e8452c", "accent_hover": "#f05a42", "stage": "#0b0c0e"}


def system_is_dark() -> bool:
    """Read the OS light/dark setting (read-only). Falls back to light."""
    try:
        if sys.platform == "win32":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize") as k:
                return winreg.QueryValueEx(k, "AppsUseLightTheme")[0] == 0
        if sys.platform == "darwin":
            import subprocess
            out = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"], capture_output=True, text=True)
            return out.stdout.strip().lower() == "dark"
    except Exception:
        pass
    return False


def palette() -> dict:
    return DARK if system_is_dark() else LIGHT


def apply_theme(root: tk.Tk, p: dict) -> None:
    """ttk 'clam' theme recolored to match the web UI. Fonts come from the system."""
    root.configure(bg=p["bg"])
    st = ttk.Style(root)
    st.theme_use("clam")
    base = ("Segoe UI", 10) if sys.platform == "win32" else ("TkDefaultFont", 11)
    st.configure(".", background=p["bg"], foreground=p["ink"], fieldbackground=p["surface2"], bordercolor=p["line"],
                 lightcolor=p["surface2"], darkcolor=p["surface2"], troughcolor=p["surface2"], font=base,
                 arrowcolor=p["ink"], focuscolor=p["accent"], insertcolor=p["ink"], selectbackground=p["accent"])
    st.configure("TFrame", background=p["bg"])
    for name, bg in (("Top", p["surface"]), ("Card", p["surface"])):
        st.configure(f"{name}.TFrame", background=bg)
    st.configure("Card.TFrame", bordercolor=p["line"], relief="solid", borderwidth=1)
    st.configure("Inner.TFrame", background=p["surface"])
    st.configure("TLabel", background=p["bg"], foreground=p["ink"])
    st.configure("Muted.TLabel", foreground=p["muted"])
    st.configure("Title.TLabel", background=p["surface"], font=(base[0], base[1] + 4, "bold"))
    st.configure("TopMuted.TLabel", background=p["surface"], foreground=p["muted"])
    st.configure("CardMuted.TLabel", background=p["surface"], foreground=p["muted"])
    st.configure("Error.TLabel", background=p["surface"], foreground=p["accent"])
    st.configure("Field.TLabel", background=p["surface"], foreground=p["muted"], font=(base[0], base[1] - 1, "bold"))
    st.configure("PaneTitle.TLabel", background=p["surface"], font=(base[0], base[1], "bold"))
    st.configure("TButton", background=p["surface2"], foreground=p["ink"], borderwidth=1, padding=(12, 6), relief="flat")
    st.map("TButton", background=[("active", p["line"])], foreground=[("disabled", p["muted"])])
    st.configure("Ghost.TButton", background=p["surface"], bordercolor=p["line"], relief="solid", borderwidth=1)
    st.map("Ghost.TButton", background=[("active", p["surface2"])])
    st.configure("Accent.TButton", background=p["accent"], foreground="#ffffff", bordercolor=p["accent"],
                 font=(base[0], base[1], "bold"))
    st.map("Accent.TButton", background=[("disabled", p["line"]), ("active", p["accent_hover"])],
           foreground=[("disabled", p["muted"])])
    st.configure("Drop.TButton", background=p["surface"], foreground=p["accent"], bordercolor=p["line"],
                 relief="solid", font=(base[0], base[1], "bold"))
    st.map("Drop.TButton", background=[("active", p["surface2"])], bordercolor=[("active", p["accent"])])
    st.configure("Card.TCheckbutton", background=p["surface"], indicatorbackground=p["surface2"],
                 indicatorforeground=p["accent"])
    st.map("Card.TCheckbutton", background=[("active", p["surface"])], indicatorbackground=[("selected", p["accent"])])
    st.configure("TCombobox", arrowsize=14, padding=4)
    st.map("TCombobox", fieldbackground=[("readonly", p["surface2"])], foreground=[("readonly", p["ink"])],
           selectbackground=[("readonly", p["surface2"])], selectforeground=[("readonly", p["ink"])])
    root.option_add("*TCombobox*Listbox.background", p["surface"])
    root.option_add("*TCombobox*Listbox.foreground", p["ink"])
    root.option_add("*TCombobox*Listbox.selectBackground", p["accent"])
    st.configure("TSpinbox", arrowsize=12, padding=4)
    st.configure("TScrollbar", background=p["line"], troughcolor=p["stage"], bordercolor=p["stage"], arrowcolor=p["muted"])
    st.configure("TPanedwindow", background=p["bg"])


def draw_logo(c: tk.Canvas) -> None:
    """The app icon (same drawing as web/icon.svg), drawn for this project."""
    c.create_rectangle(0, 0, 28, 28, fill="#e8452c", outline="")
    for x, w, shade in ((4, 4, "#ffffff"), (10, 4, "#fbd9d3"), (16, 4, "#f6b3a8"), (22, 2, "#f28d7d")):
        c.create_rectangle(x, 7, x + w, 21, fill=shade, outline="")


def system_language() -> str:
    """'ko' when the OS UI language is Korean, else 'en'. Read-only; nothing is changed."""
    try:
        if sys.platform == "win32":
            import ctypes
            return "ko" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x12 else "en"
        if sys.platform == "darwin":
            import subprocess
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"], capture_output=True, text=True).stdout
            first = out.strip("()\n ").split(",")[0].strip().strip('"')
            return "ko" if first.lower().startswith("ko") else "en"
        import os
        for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
            if os.environ.get(var):
                return "ko" if os.environ[var].lower().startswith("ko") else "en"
    except Exception:
        pass
    return "en"


def enable_high_dpi() -> None:
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


class ScrollView(ttk.Frame):
    """A canvas with horizontal and vertical scrollbars showing one image."""

    def __init__(self, master, title_var: tk.StringVar):
        super().__init__(master, style="Card.TFrame", padding=10)
        ttk.Label(self, textvariable=title_var, style="PaneTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.canvas = tk.Canvas(self, bg=PREVIEW_BG, highlightthickness=0, bd=0)
        xs = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        ys = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        ys.grid(row=1, column=1, sticky="ns")
        xs.grid(row=2, column=0, sticky="ew")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self._photo = None
        # Wheel scrolls vertically, Shift+wheel horizontally (Windows/macOS and X11 buttons).
        self.canvas.bind("<MouseWheel>", lambda e: self._wheel(e, "y"))
        self.canvas.bind("<Shift-MouseWheel>", lambda e: self._wheel(e, "x"))
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))
        self.canvas.bind("<Shift-Button-4>", lambda e: self.canvas.xview_scroll(-3, "units"))
        self.canvas.bind("<Shift-Button-5>", lambda e: self.canvas.xview_scroll(3, "units"))

    def _wheel(self, event, axis):
        step = -1 * (event.delta // 120 or (1 if event.delta > 0 else -1)) * 3
        (self.canvas.yview_scroll if axis == "y" else self.canvas.xview_scroll)(step, "units")

    def show(self, img: Image.Image | None, text: str = ""):
        self.canvas.delete("all")
        if img is None:
            self._photo = None
            self.canvas.create_text(20, 20, anchor="nw", text=text, fill="#aab")
            self.canvas.configure(scrollregion=(0, 0, 1, 1))
            return
        self._photo = ImageTk.PhotoImage(img)
        vw, vh = self.viewport()
        # Center when smaller than the view; scroll region still covers the image when larger.
        x, y = max(0, (vw - img.width) // 2), max(0, (vh - img.height) // 2)
        self.canvas.create_image(x, y, anchor="nw", image=self._photo)
        self.canvas.configure(scrollregion=(0, 0, max(vw, x + img.width), max(vh, y + img.height)))

    def viewport(self) -> tuple[int, int]:
        return max(50, self.canvas.winfo_width()), max(50, self.canvas.winfo_height())


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        try:  # window/taskbar icon, same drawing as web/icon.svg (tools/make_icon.py)
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
            self._icon = tk.PhotoImage(file=str(base / "web" / "icon.png"))
            root.iconphoto(True, self._icon)
        except Exception:
            pass
        self.lang = system_language()
        self.src_path: Path | None = None
        self.src: Image.Image | None = None
        self.result_dir: Path | None = None
        self.jobs: queue.Queue = queue.Queue()
        self.saving = False

        self.count = tk.IntVar(value=core.DEFAULT_STRIPS)
        self.optimize = tk.BooleanVar(value=True)
        self.zoom = tk.StringVar(value="fit")
        self.status = tk.StringVar()
        self.src_title = tk.StringVar()
        self.prev_title = tk.StringVar()

        pal = self.pal = palette()
        apply_theme(root, pal)

        top = ttk.Frame(root, style="Top.TFrame", padding=(16, 10))
        top.pack(fill="x")
        brand = ttk.Frame(top, style="Top.TFrame")
        brand.pack(side="left")
        self.logo = tk.Canvas(brand, width=28, height=28, highlightthickness=0, bg=pal["surface"])
        draw_logo(self.logo)
        self.logo.pack(side="left", padx=(0, 10))
        ttk.Label(brand, text="Scrollfold", style="Title.TLabel").pack(anchor="w")
        self.l_tag = ttk.Label(brand, style="TopMuted.TLabel")
        self.l_tag.pack(anchor="w")
        self.b_lang = ttk.Button(top, command=self.toggle_lang, style="Ghost.TButton")
        self.b_lang.pack(side="right")
        self.b_credits = ttk.Button(top, command=self.show_credits, style="Ghost.TButton")
        self.b_credits.pack(side="right", padx=6)

        body = ttk.Frame(root, padding=14)
        body.pack(fill="both", expand=True)
        side = ttk.Frame(body, style="Card.TFrame", padding=16)
        side.pack(side="left", fill="y", padx=(0, 14))

        self.b_open = ttk.Button(side, command=self.open_image, style="Drop.TButton")
        self.b_open.pack(fill="x", ipady=14)
        self.l_file = ttk.Label(side, style="CardMuted.TLabel", width=30)
        self.l_file.pack(fill="x", pady=(4, 0))
        self.l_accepts = ttk.Label(side, style="CardMuted.TLabel", wraplength=230, justify="left",
                                   font=("Segoe UI", 8) if sys.platform == "win32" else ("TkDefaultFont", 9))
        self.l_accepts.pack(fill="x", pady=(2, 12))

        self.l_count = ttk.Label(side, style="Field.TLabel")
        self.l_count.pack(anchor="w")
        row = ttk.Frame(side, style="Inner.TFrame")
        row.pack(fill="x", pady=(4, 12))
        self.spin = ttk.Spinbox(row, from_=core.MIN_STRIPS, to=core.MAX_STRIPS, width=5,
                                textvariable=self.count, command=self.redraw)
        self.spin.pack(side="left")
        self.spin.bind("<Return>", lambda e: self.redraw())
        self.spin.bind("<FocusOut>", lambda e: self.redraw())
        self.b_auto = ttk.Button(row, command=self.auto_count)
        self.b_auto.pack(side="left", padx=(8, 0))

        self.l_ratio = ttk.Label(side, style="Field.TLabel")
        self.l_ratio.pack(anchor="w")
        self.ratio_box = ttk.Combobox(side, state="readonly")
        self.ratio_box.pack(fill="x", pady=(4, 12))
        self.ratio_box.bind("<<ComboboxSelected>>", lambda e: self.auto_count())

        self.l_fit = ttk.Label(side, style="Field.TLabel")
        self.l_fit.pack(anchor="w")
        self.fit_box = ttk.Combobox(side, state="readonly")
        self.fit_box.pack(fill="x", pady=(4, 12))
        self.fit_box.bind("<<ComboboxSelected>>", lambda e: self.redraw())

        self.c_opt = ttk.Checkbutton(side, variable=self.optimize, style="Card.TCheckbutton")
        self.c_opt.pack(anchor="w", pady=(0, 16))

        self.b_save = ttk.Button(side, command=self.save, state="disabled", style="Accent.TButton")
        self.b_save.pack(fill="x", ipady=4)
        self.b_folder = ttk.Button(side, command=self.open_folder, state="disabled", style="Ghost.TButton")
        self.b_folder.pack(fill="x", pady=(8, 0))
        self.b_cancel = ttk.Button(side, command=self.cancel_save, style="Ghost.TButton")
        self.l_status = ttk.Label(side, textvariable=self.status, style="CardMuted.TLabel", wraplength=230, justify="left")
        self.l_status.pack(fill="x", pady=(12, 0))
        self.l_keys = ttk.Label(side, style="CardMuted.TLabel", wraplength=230, justify="left",
                                font=("Segoe UI", 8) if sys.platform == "win32" else ("TkDefaultFont", 9))
        self.l_keys.pack(side="bottom", fill="x")

        views = ttk.Frame(body)
        views.pack(side="left", fill="both", expand=True)
        zbar = ttk.Frame(views)
        zbar.pack(fill="x", pady=(0, 8))
        self.zoom_box = ttk.Combobox(zbar, textvariable=self.zoom, width=7, state="readonly")
        self.zoom_box.pack(side="right")
        self.zoom_box.bind("<<ComboboxSelected>>", lambda e: self.redraw())
        self.l_zoom = ttk.Label(zbar, style="Muted.TLabel")
        self.l_zoom.pack(side="right", padx=6)
        panes = ttk.PanedWindow(views, orient="vertical")
        panes.pack(fill="both", expand=True)
        self.src_view = ScrollView(panes, self.src_title)
        self.prev_view = ScrollView(panes, self.prev_title)
        panes.add(self.src_view, weight=1)
        panes.add(self.prev_view, weight=1)

        root.bind_all("<Control-o>", lambda e: self.open_image())
        root.bind_all("<Control-s>", lambda e: self.save())
        root.bind_all("<Control-e>", lambda e: self.open_folder())
        root.bind_all("<Escape>", lambda e: self.cancel_save())
        self.cancel_event = threading.Event()
        root.bind("<Configure>", self._on_resize)
        self._resize_job = None
        self.apply_lang()

    # ------------------------------------------------------------ text
    def tr(self, key, **kw):
        return t(self.lang, key, **kw)

    def apply_lang(self):
        self.root.title(self.tr("title"))
        self.b_open.configure(text=self.tr("open"))
        self.l_count.configure(text=self.tr("count"))
        self.c_opt.configure(text=self.tr("optimize"))
        self.b_auto.configure(text=self.tr("auto"))
        self.l_ratio.configure(text=self.tr("ratio"))
        self.l_fit.configure(text=self.tr("fit_mode"))
        for box, keys, default in ((self.ratio_box, list(core.RATIOS), core.DEFAULT_RATIO),
                                   (self.fit_box, list(core.FIT_MODES), core.DEFAULT_FIT)):
            cur = box.current() if box.get() else keys.index(default)
            box.configure(values=[self.tr("ratio_" + k) if k == "original" else
                                  (self.tr("fit_" + k) if box is self.fit_box else f"{k}  ·  {self.tr('hint_' + k)}")
                                  for k in keys])
            box.current(cur)
        self.l_zoom.configure(text=self.tr("zoom"))
        labels = [self.tr("fit") if z == "fit" else z for z in ZOOMS]
        cur = self.zoom_box.current() if self.zoom_box.get() else 0
        self.zoom_box.configure(values=labels)
        self.zoom_box.current(max(0, cur))
        self.b_save.configure(text=self.tr("save"))
        self.b_folder.configure(text=self.tr("open_folder"))
        self.b_lang.configure(text=self.tr("lang"))
        self.b_credits.configure(text=self.tr("credits"))
        self.b_cancel.configure(text=self.tr("cancel"))
        self.l_accepts.configure(text=self.tr("accepts", formats=core.DESKTOP_FORMATS))
        self.l_keys.configure(text=self.tr("shortcuts"))
        self.l_tag.configure(text=self.tr("tagline"))
        if self.src_path is None:
            self.l_file.configure(text=self.tr("hint"))
        self.src_title.set(self.tr("source"))
        self.prev_title.set(self.tr("preview"))
        self.redraw()

    def show_credits(self):
        messagebox.showinfo(self.tr("credits"), self.tr("credits_body"))

    def toggle_lang(self):
        self.lang = "ko" if self.lang == "en" else "en"
        self.apply_lang()

    # ------------------------------------------------------------ actions
    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[
            (self.tr("filetypes"), "*.png *.jpg *.jpeg *.webp *.avif *.gif *.bmp *.tif *.tiff *.tga *.jp2 *.j2k *.qoi *.ppm *.pcx *.ico"),
            (self.tr("allfiles"), "*.*")])
        if path:
            self.load(Path(path))
        self.b_open.focus_set()

    def load(self, path: Path):
        try:
            self.src = core.open_image(path)
        except Exception as err:  # bad file, too large, unsupported format: shown inline, no dialog
            self.show_error(err)
            return
        self.src_path = path
        self.l_file.configure(text=path.name)
        # Working copy for previews, capped so huge images stay responsive.
        w, h = self.src.size
        b = min(1.0, MAX_VIEW_SIDE / max(w, h))
        base = self.src if b == 1 else self.src.resize((max(1, round(w * b)), max(1, round(h * b))), Image.BILINEAR)
        self.base = base.convert("RGB")
        self.result_dir = None
        self.b_folder.configure(state="disabled")
        self.b_save.configure(state="normal")
        self.auto_count()

    def ratio(self):
        return core.RATIOS[list(core.RATIOS)[max(0, self.ratio_box.current())]]

    def fit_mode(self) -> str:
        return core.FIT_MODES[max(0, self.fit_box.current())]

    def auto_count(self):
        if self.src is not None:
            self.count.set(core.suggest_count(*self.src.size, self.ratio()))
        self.redraw()

    def current_count(self) -> int:
        try:
            n = int(self.spin.get())
        except ValueError:
            n = core.DEFAULT_STRIPS
        n = min(core.MAX_STRIPS, max(core.MIN_STRIPS, n))
        self.count.set(n)
        return n

    def scale_for(self, w: int, h: int, view: ScrollView, extra_w: int = 0) -> float:
        idx = self.zoom_box.current()
        if idx <= 0:
            vw, vh = view.viewport()
            s = min((vw - extra_w - 4) / w, (vh - 4) / h)
        else:
            s = int(ZOOMS[idx].rstrip("%")) / 100
        return max(0.001, min(s, MAX_VIEW_SIDE / max(w, h)))

    def redraw(self):
        if self.src is None:
            self.src_view.show(None, self.tr("hint"))
            self.prev_view.show(None, "")
            if self.l_status.cget("style") != "Error.TLabel":  # keep an open error visible
                self.set_status(self.tr("hint"))
            return
        n = self.current_count()
        ratio, mode = self.ratio(), self.fit_mode()
        w, h = self.src.size
        # Full-size numbers for the status line.
        if ratio is None:
            fw, fh = w, h
        elif mode == "crop":
            x0, y0, x1, y1 = core.crop_box(w, h, core.target_aspect(n, ratio))
            fw, fh = x1 - x0, y1 - y0
        else:
            fw, fh = core.pad_size(w, h, core.target_aspect(n, ratio))
        try:
            core.strip_boxes(fw, fh, n)
            fitted = core.fit_image(self.base, n, ratio, mode)
            boxes = core.strip_boxes(fitted.width, fitted.height, n)
        except core.SplitError as err:
            self.show_error(err)
            return

        # Source pane. Crop: original with the dropped area dimmed. Pad: the padded canvas.
        if ratio is not None and mode == "crop":
            shown = self.base
            cx0, cy0, _, _ = core.crop_box(self.base.width, self.base.height, core.target_aspect(n, ratio))
        else:
            shown, cx0, cy0 = fitted, 0, 0
        s = self.scale_for(shown.width, shown.height, self.src_view)
        view = shown.resize((max(1, round(shown.width * s)), max(1, round(shown.height * s))), Image.BILINEAR)
        if shown is self.base and fitted.size != self.base.size:
            keep = (round(cx0 * s), round(cy0 * s), round((cx0 + fitted.width) * s), round((cy0 + fitted.height) * s))
            bright = view.crop(keep)
            view = Image.blend(view, Image.new("RGB", view.size, (0, 0, 0)), 0.65)
            view.paste(bright, keep[:2])
        draw = ImageDraw.Draw(view)
        for bx0, _, bx1, _ in boxes:
            for x in (bx0, bx1):
                X = round((x + cx0) * s)
                draw.line([(X, round(cy0 * s)), (X, round((cy0 + fitted.height) * s))], fill=LINE_COLOR, width=2)
        self.src_view.show(view)

        # Strips laid out with gaps, like a multi-image post.
        sw = boxes[0][2] - boxes[0][0]
        s2 = self.scale_for(sw * n, fitted.height, self.prev_view, extra_w=GAP * (n - 1))
        tw, th = max(1, int(sw * s2)), max(1, int(fitted.height * s2))  # floor so "Fit" never overflows
        sheet = Image.new("RGB", (tw * n + GAP * (n - 1), th), PREVIEW_BG)
        for i, box in enumerate(boxes):
            sheet.paste(fitted.crop(box).resize((tw, th), Image.BILINEAR), (i * (tw + GAP), 0))
        self.prev_view.show(sheet)

        msg = self.tr("loaded", name=self.src_path.name, w=w, h=h, n=n, sw=fw // n, sh=fh)
        if w * h > core.LARGE_WARN_PIXELS:
            msg += " · ⚠ " + self.tr("large", mp=round(w * h / 1e6))
        if ratio is not None and mode == "crop" and (fw, fh) != (w, h):
            msg += " · " + self.tr("kept", pct=round(100 * fw * fh / (w * h)))
        self.set_status(msg)

    def _on_resize(self, event):
        # The canvases count too: at startup they get their real size only after the first draw,
        # and dragging the divider between the panes resizes them without resizing the window.
        watched = (self.root, self.src_view.canvas, self.prev_view.canvas)
        if any(event.widget is w for w in watched) and self.zoom_box.current() <= 0:
            if self._resize_job:
                self.root.after_cancel(self._resize_job)
            self._resize_job = self.root.after(200, self.redraw)

    def save(self):
        if self.src_path is None:
            return
        if self.saving:
            self.set_status(self.tr("busy"))
            return
        self.saving = True
        self.cancel_event.clear()
        self.b_save.configure(state="disabled")
        self.b_cancel.pack(fill="x", pady=(8, 0), after=self.b_save)
        args = (self.src_path, self.current_count(), self.optimize.get())
        ratio, mode = self.ratio(), self.fit_mode()
        out = core.output_root()
        expected = core.unique_dir(out, core.safe_name(self.src_path.stem))

        def work():
            try:
                folder, files = core.split_file(*args, out_base=out,
                                                progress=lambda i, n: self.jobs.put(("progress", i, n)),
                                                ratio=ratio, mode=mode, cancel=self.cancel_event)
                self.jobs.put(("done", folder, len(files)))
            except core.Cancelled as c:
                self.jobs.put(("cancelled", len(c.saved), args[1], expected))
            except Exception as err:
                self.jobs.put(("error", err))

        threading.Thread(target=work, daemon=True).start()
        self.root.after(100, self.poll)

    def poll(self):
        try:
            while True:
                msg = self.jobs.get_nowait()
                if msg[0] == "progress":
                    self.set_status(self.tr("saving", i=msg[1], n=msg[2]))
                elif msg[0] == "done":
                    self.saving = False
                    self.result_dir = msg[1]
                    self.set_status(self.tr("saved", n=msg[2], path=msg[1]))
                    self.end_save()
                    self.b_folder.configure(state="normal")
                    return
                elif msg[0] == "cancelled":
                    n, total, folder = msg[1], msg[2], msg[3]
                    if n:
                        self.result_dir = folder
                        self.b_folder.configure(state="normal")
                    self.set_status(self.tr("cancelled", n=n, total=total, path=folder) if n else self.tr("cancelled_none"))
                    self.end_save()
                    return
                else:
                    self.end_save()
                    self.show_error(msg[1])
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def end_save(self):
        self.saving = False
        self.b_save.configure(state="normal")
        self.b_cancel.pack_forget()
        self.b_save.focus_set()

    def cancel_save(self):
        if self.saving:
            self.cancel_event.set()

    def set_status(self, text: str, error: bool = False):
        self.status.set(text)
        self.l_status.configure(style="Error.TLabel" if error else "CardMuted.TLabel")

    def show_error(self, err: Exception):
        """Specific, translated message shown inline (no pop-up)."""
        key, info = core.describe_error(err)
        self.set_status(self.tr(key, **info), error=True)

    def open_folder(self):
        if self.result_dir and self.result_dir.exists():
            core.open_in_file_manager(self.result_dir)


def smoke(folder: str) -> int:
    """Headless check for build.bat: split a generated image and verify the files."""
    work = Path(folder)
    try:
        src = work / "smoke.png"
        Image.new("RGB", (2003, 300), "red").save(src)
        out, files = core.split_file(src, core.DEFAULT_STRIPS, True, work / "out")
        assert len(files) == core.DEFAULT_STRIPS and all(p.stat().st_size > 0 for p in files)
        return 0
    except Exception as err:
        (work / "smoke.log").write_text(repr(err), encoding="utf-8")
        return 1


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--smoke":
        sys.exit(smoke(sys.argv[2]))
    enable_high_dpi()
    root = tk.Tk()
    root.geometry("1200x800")
    root.minsize(640, 480)
    app = App(root)
    if len(sys.argv) == 2 and Path(sys.argv[1]).is_file():
        root.after(100, lambda: app.load(Path(sys.argv[1])))
    root.mainloop()


if __name__ == "__main__":
    main()
