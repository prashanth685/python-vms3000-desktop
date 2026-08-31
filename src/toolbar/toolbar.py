"""
toolbar.py — VMS 3000  •  Professional toolbar
Dark-title-strip + light icon band.  Groups separated by hairline rules.
"""

import tkinter as tk
from theme  import T
from icons  import IconPainter
from tooltip import ToolTip

# Icon groups: list of (key, tooltip)
_GROUPS = [
    [
        ("new",      "New File          (Ctrl+N)"),
        ("open",     "Open…             (Ctrl+O)"),
        ("save",     "Save              (Ctrl+S)"),
        ("print",    "Print…            (Ctrl+P)"),
    ],
    [
        ("cut",      "Cut               (Ctrl+X)"),
        ("copy",     "Copy              (Ctrl+C)"),
        ("paste",    "Paste             (Ctrl+V)"),
    ],
    [
        ("upload",   "Upload to Device"),
        ("download", "Download from Device"),
        ("refresh",  "Refresh / Rescan"),
    ],
    [
        ("settings", "Preferences"),
        ("key",      "License / Key"),
        ("help",     "Help              (F1)"),
    ],
]


def build_toolbar(root, fonts, rack_addr_var: tk.StringVar):
    icons = IconPainter(T["toolbar_bg"])

    # ── Outer container (provides the 1 px bottom border) ──────────────────
    outer = tk.Frame(root, bg=T["toolbar_border"], bd=0)
    outer.pack(side="top", fill="x")

    # ── Title strip  (dark navy, 36 px tall) ───────────────────────────────
    title_strip = tk.Frame(outer, bg=T["titlebar"], height=36)
    title_strip.pack(fill="x", padx=0)
    title_strip.pack_propagate(False)

    tk.Label(
        title_strip,
        text="VMS 3000  —  Rack Configuration Software  v0.5",
        font=fonts["ui_b"],
        bg=T["titlebar"],
        fg="#a8c8e8",
        anchor="w",
    ).pack(side="left", padx=12, pady=4)

    tk.Label(
        title_strip,
        text="Sarayu Infotech Solutions Pvt Ltd",
        font=fonts["ui"],
        bg=T["titlebar"],
        fg="#7090b0",
        anchor="e",
    ).pack(side="right", padx=12, pady=4)

    # ── Icon band ──────────────────────────────────────────────────────────
    tb = tk.Frame(outer, bg=T["toolbar_bg"], pady=6)
    tb.pack(fill="x", pady=(0, 1))

    # Left padding
    tk.Frame(tb, bg=T["toolbar_bg"], width=6).pack(side="left")

    for g_idx, group in enumerate(_GROUPS):
        if g_idx:
            _sep(tb)
        for key, tip in group:
            _icon_btn(tb, icons, key, tip)

    # Right-side controls
    _sep(tb)
    _badge(tb, fonts)
    _sep(tb)
    _rack_addr_entry(tb, fonts, rack_addr_var)

    return icons


# ── Helpers ────────────────────────────────────────────────────────────────

def _sep(parent: tk.Frame) -> None:
    """Hairline vertical separator."""
    tk.Frame(parent, bg=T["toolbar_sep"], width=1).pack(
        side="left", fill="y", padx=7, pady=5
    )


def _badge(parent: tk.Frame, fonts: dict) -> None:
    """VMS 3000 badge pill."""
    badge = tk.Frame(
        parent,
        bg=T["titlebar"],
        padx=12,
        pady=4,
    )
    badge.pack(side="left", padx=6)
    tk.Label(
        badge,
        text="VMS 3000",
        font=fonts["vms"],
        bg=T["titlebar"],
        fg="#ffffff",
    ).pack()


def _rack_addr_entry(parent: tk.Frame, fonts: dict, var: tk.StringVar) -> None:
    tk.Label(
        parent,
        text="Rack Address",
        font=fonts["ui"],
        bg=T["toolbar_bg"],
        fg=T["text_dim"],
    ).pack(side="left", padx=(6, 4))

    tk.Entry(
        parent,
        textvariable=var,
        width=6,
        font=fonts["ui_b"],
        bg="#ffffff",
        fg=T["text"],
        relief="sunken",
        bd=2,
        insertbackground=T["accent"],
        justify="center",
    ).pack(side="left", padx=(0, 10))


def _icon_btn(parent: tk.Frame, icons: IconPainter, key: str, tip: str) -> tk.Label:
    img = icons.get(key)
    btn = tk.Label(
        parent,
        image=img,
        bg=T["toolbar_bg"],
        cursor="hand2",
        padx=6,
        pady=4,
        relief="solid",
        bd=1,
        highlightbackground=T["toolbar_border"],
        highlightthickness=1,
    )
    btn.image = img
    btn.pack(side="left", padx=2)

    def _enter(e):
        btn.config(bg=T["btn_hover"], relief="solid", highlightbackground=T["accent"])

    def _leave(e):
        btn.config(bg=T["toolbar_bg"], relief="solid", highlightbackground=T["toolbar_border"])

    def _press(e):
        btn.config(bg=T["btn_press"], relief="sunken", highlightbackground=T["accent"])

    def _release(e):
        btn.config(bg=T["btn_hover"], relief="solid", highlightbackground=T["accent"])

    btn.bind("<Enter>",            _enter)
    btn.bind("<Leave>",            _leave)
    btn.bind("<ButtonPress-1>",    _press)
    btn.bind("<ButtonRelease-1>",  _release)

    ToolTip(btn, tip)
    return btn