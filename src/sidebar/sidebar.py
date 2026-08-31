"""
sidebar.py — VMS 3000  •  Professional navy sidebar
Fixed 148 px wide.  Section header + labelled nav buttons + bottom brand block.
"""

import tkinter as tk
import tkinter.font as tkfont
from theme import T

_NAV_ITEMS = [
    # (label, sub-label, cmd_key)
    ("Rack Setup",  "Configure slots",  "rack_setup"),
    ("Load",        "Open config file", "load"),
    ("Save",        "Save config file", "save"),
]


def build_sidebar(parent, fonts: dict, commands: dict) -> tk.Frame:
    sb = tk.Frame(parent, bg=T["sidebar_bg"], width=220)
    sb.pack(side="left", fill="y")
    sb.pack_propagate(False)

    # ── Top accent line ────────────────────────────────────────────
    tk.Frame(sb, bg=T["accent_teal"], height=3).pack(fill="x")

    # ── Section header ─────────────────────────────────────────────
    hdr = tk.Frame(sb, bg=T["sidebar_dark"], pady=14)
    hdr.pack(fill="x")
    tk.Label(
        hdr,
        text="N A V I G A T I O N",
        font=tkfont.Font(family="Segoe UI", size=8, weight="bold"),
        bg=T["sidebar_dark"],
        fg="#5a7a9a",
    ).pack(padx=12, anchor="w")

    # ── Nav buttons ────────────────────────────────────────────────
    for label, sublabel, key in _NAV_ITEMS:
        _nav_btn(sb, fonts, label, sublabel, commands.get(key))
        tk.Frame(sb, bg=T["sidebar_rule"], height=1).pack(fill="x", padx=8, pady=4)

    # ── Spacer ─────────────────────────────────────────────────────
    tk.Frame(sb, bg=T["sidebar_bg"]).pack(fill="both", expand=True)

    # ── Status section ─────────────────────────────────────────────
    _status_block(sb, fonts)

    # ── Bottom brand ───────────────────────────────────────────────
    _brand_block(sb, fonts)

    return sb


def _nav_btn(parent: tk.Frame, fonts: dict, label: str, sublabel: str, cmd) -> None:
    """Two-line nav button with hover highlight."""
    btn_frame = tk.Frame(parent, bg=T["sidebar_btn"], cursor="hand2")
    btn_frame.pack(fill="x", padx=0, pady=4)

    inner = tk.Frame(btn_frame, bg=T["sidebar_btn"], padx=12, pady=10)
    inner.pack(fill="x")

    lbl_main = tk.Label(
        inner,
        text=label,
        font=fonts["ui_b"],
        bg=T["sidebar_btn"],
        fg=T["sidebar_text_hi"],
        anchor="w",
    )
    lbl_main.pack(fill="x")

    lbl_sub = tk.Label(
        inner,
        text=sublabel,
        font=tkfont.Font(family="Segoe UI", size=8),
        bg=T["sidebar_btn"],
        fg=T["sidebar_text"],
        anchor="w",
    )
    lbl_sub.pack(fill="x")

    # Left accent bar (hidden by default, shown on hover/press)
    accent = tk.Frame(btn_frame, bg=T["sidebar_btn"], width=4)
    accent.place(x=0, y=0, relheight=1)

    widgets = [btn_frame, inner, lbl_main, lbl_sub, accent]

    def _enter(e):
        for w in widgets:
            w.config(bg=T["sidebar_btn_h"])
        accent.config(bg=T["accent"])

    def _leave(e):
        for w in widgets:
            w.config(bg=T["sidebar_btn"])
        accent.config(bg=T["sidebar_btn"])

    def _press(e):
        for w in widgets:
            w.config(bg=T["sidebar_btn_p"])

    def _release(e):
        for w in widgets:
            w.config(bg=T["sidebar_btn_h"])
        if cmd:
            cmd()

    for w in [btn_frame, inner, lbl_main, lbl_sub]:
        w.bind("<Enter>",           _enter)
        w.bind("<Leave>",           _leave)
        w.bind("<ButtonPress-1>",   _press)
        w.bind("<ButtonRelease-1>", _release)


def _status_block(parent: tk.Frame, fonts: dict) -> None:
    """Small connection status indicator."""
    blk = tk.Frame(parent, bg=T["sidebar_dark"], pady=12, padx=12)
    blk.pack(fill="x")

    tk.Label(
        blk,
        text="DEVICE STATUS",
        font=tkfont.Font(family="Segoe UI", size=8, weight="bold"),
        bg=T["sidebar_dark"],
        fg="#5a7a9a",
    ).pack(anchor="w")

    row = tk.Frame(blk, bg=T["sidebar_dark"])
    row.pack(anchor="w", pady=(8, 0))

    tk.Label(row, text="●", font=tkfont.Font(size=10),
             bg=T["sidebar_dark"], fg=T["led_red"]).pack(side="left")
    tk.Label(row, text="  Not Connected",
             font=tkfont.Font(family="Segoe UI", size=9),
             bg=T["sidebar_dark"], fg=T["sidebar_text"]).pack(side="left")


def _brand_block(parent: tk.Frame, fonts: dict) -> None:
    brand = tk.Frame(parent, bg=T["sidebar_dark"], pady=14)
    brand.pack(fill="x")

    tk.Frame(brand, bg=T["accent_teal"], height=1).pack(fill="x", pady=(0, 10))

    tk.Label(
        brand,
        text="SARAYU INFOTECH",
        font=tkfont.Font(family="Segoe UI", size=8, weight="bold"),
        bg=T["sidebar_dark"],
        fg="#5a7a9a",
    ).pack()

    tk.Label(
        brand,
        text="SOLUTIONS PVT LTD",
        font=tkfont.Font(family="Segoe UI", size=8),
        bg=T["sidebar_dark"],
        fg="#465e76",
    ).pack()