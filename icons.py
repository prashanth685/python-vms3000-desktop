"""
icons.py — VMS 3000 toolbar icon painter
Uses MaterialIcons-Regular.ttf (place alongside this file or in an 'icons/' sub-folder).

Each icon is rendered at SZ×SZ onto the toolbar background colour, using the
slate icon colour so everything looks uniform and crisp.
"""

import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ── Icon codepoint map ────────────────────────────────────────────────────────
# Material Icons Unicode codepoints (confirmed from codepoints file)
_CODEPOINTS: dict[str, str] = {
    "add":            "\ue145",
    "folder_open":    "\ue2c7",
    "save":           "\ue161",
    "print":          "\ue8ad",
    "settings":       "\ue8b8",
    "content_cut":    "\ue14e",
    "content_copy":   "\ue14d",
    "content_paste":  "\ue14f",
    "upload":         "\ue2c6",
    "download":       "\ue2c4",
    "refresh":        "\ue5d5",
    "vpn_key":        "\ue0da",
    "help":           "\ue887",
    "note_add":       "\ue89c",
    "description":    "\ue873",
}

# Toolbar key  →  (codepoint_key, label_for_debug)
_ICON_MAP: dict[str, str] = {
    "new":      "note_add",
    "open":     "folder_open",
    "save":     "save",
    "print":    "print",
    "settings": "settings",
    "cut":      "content_cut",
    "copy":     "content_copy",
    "paste":    "content_paste",
    "upload":   "upload",
    "download": "download",
    "refresh":  "refresh",
    "key":      "vpn_key",
    "help":     "help",
}

# ── Colour constants — keep in sync with theme.py ────────────────────────────
_ICON_COLOUR   = "#475569"   # slate-600
_DEFAULT_BG    = "#f4f6f9"


def _find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Search common locations for MaterialIcons-Regular.ttf."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "MaterialIcons-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "icons", "MaterialIcons-Regular.ttf"),
        "MaterialIcons-Regular.ttf",
        r"C:\Windows\Fonts\MaterialIcons-Regular.ttf",
        "/usr/share/fonts/truetype/material-design-icons/MaterialIcons-Regular.ttf",
        "/usr/share/fonts/MaterialIcons-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    print("⚠️  MaterialIcons-Regular.ttf not found — place it alongside icons.py")
    return ImageFont.load_default()


class IconPainter:
    """Render Material Icons glyphs as PhotoImages for the toolbar."""

    SZ = 26   # rendered glyph size (pixels)
    PAD = 3   # extra transparent padding each side → final image = SZ + PAD*2

    def __init__(self, bg_hex: str = _DEFAULT_BG):
        self.bg_hex = bg_hex
        self._cache: dict[str, ImageTk.PhotoImage] = {}
        self._font  = _find_font(self.SZ)

    # ── public ──────────────────────────────────────────────────────────────
    def get(self, name: str) -> ImageTk.PhotoImage:
        if name not in self._cache:
            self._cache[name] = self._render(name)
        return self._cache[name]

    # ── internals ───────────────────────────────────────────────────────────
    def _render(self, name: str) -> ImageTk.PhotoImage:
        cp_key = _ICON_MAP.get(name)
        char   = _CODEPOINTS.get(cp_key, "\ue000") if cp_key else "\ue000"

        total  = self.SZ + self.PAD * 2
        img    = Image.new("RGB", (total, total), self.bg_hex)
        draw   = ImageDraw.Draw(img)

        try:
            draw.text(
                (total // 2, total // 2),
                char,
                font=self._font,
                fill=_ICON_COLOUR,
                anchor="mm",
            )
            print(f"[OK] icon [{name}]")
        except Exception as exc:
            print(f"[WARN] icon [{name}]: {exc}")
            self._draw_fallback_glyph(draw, total)

        return ImageTk.PhotoImage(img)

    def _draw_fallback_glyph(self, draw: ImageDraw.ImageDraw, sz: int) -> None:
        """Draw a simple square placeholder when the glyph fails."""
        m = sz // 4
        r, g, b = int(_ICON_COLOUR[1:3], 16), int(_ICON_COLOUR[3:5], 16), int(_ICON_COLOUR[5:7], 16)
        fill = (r, g, b)
        draw.rectangle([m, m, sz - m, sz - m], fill=fill)

    def _fallback(self) -> ImageTk.PhotoImage:
        """Tkinter PhotoImage fallback (no PIL rendering path)."""
        sz  = self.SZ + self.PAD * 2
        img = tk.PhotoImage(width=sz, height=sz)
        img.put(self.bg_hex, to=(0, 0, sz, sz))
        m   = sz // 4
        for y in range(m, sz - m):
            for x in range(m, sz - m):
                img.put(_ICON_COLOUR, to=(x, y, x + 1, y + 1))
        return img