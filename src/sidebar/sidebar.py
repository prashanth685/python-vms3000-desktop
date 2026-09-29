"""
sidebar.py — VMS 3000 • Professional navy sidebar
Modern navigation buttons with unique accent colors.
"""

import tkinter as tk
import tkinter.font as tkfont
from theme import T


_NAV_ITEMS = [
    # (label, sub-label, cmd_key, accent_color)
    ("Rack Setup",  "Configure slots",  "rack_setup", "#19C3B1"),  # Teal
    ("Load",        "Open config file", "load",       "#4F8CFF"),  # Blue
    ("Save",        "Save config file", "save",       "#A56EFF"),  # Purple
]


def build_sidebar(parent, fonts: dict, commands: dict) -> tk.Frame:
    sb = tk.Frame(
        parent,
        bg=T["sidebar_bg"],
        width=220
    )
    sb.pack(side="left", fill="y")
    sb.pack_propagate(False)

    # ── Top accent line ────────────────────────────────────────────
    tk.Frame(
        sb,
        bg=T["accent_teal"],
        height=3
    ).pack(fill="x")

    # ── Section header ────────────────────────────────────────────
    hdr = tk.Frame(
        sb,
        bg=T["sidebar_dark"],
        pady=14
    )
    hdr.pack(fill="x")

    tk.Label(
        hdr,
        text="N A V I G A T I O N",
        font=tkfont.Font(
            family="Segoe UI",
            size=8,
            weight="bold"
        ),
        bg=T["sidebar_dark"],
        fg="#6B87A3",
    ).pack(padx=14, anchor="w")

    # ── Navigation buttons ───────────────────────────────────────
    for label, sublabel, key, accent_color in _NAV_ITEMS:
        _nav_btn(
            sb,
            fonts,
            label,
            sublabel,
            commands.get(key),
            accent_color
        )

    # ── Spacer ────────────────────────────────────────────────────
    tk.Frame(
        sb,
        bg=T["sidebar_bg"]
    ).pack(fill="both", expand=True)

    # ── Status section ────────────────────────────────────────────
    _status_block(sb, fonts)

    # ── Bottom brand ──────────────────────────────────────────────
    _brand_block(sb, fonts)

    return sb


def _nav_btn(
    parent: tk.Frame,
    fonts: dict,
    label: str,
    sublabel: str,
    cmd,
    accent_color: str
) -> None:
    """
    Modern two-line navigation button.

    Each button has:
      • Unique accent color
      • Dark card background
      • Hover highlight
      • Pressed state
      • Colored left indicator
      • Subtle visual separation
    """

    normal_bg = "#172A3D"
    hover_bg = "#20384F"
    pressed_bg = "#102235"

    # Outer card
    btn_frame = tk.Frame(
        parent,
        bg=normal_bg,
        cursor="hand2",
        height=62
    )
    btn_frame.pack(
        fill="x",
        padx=8,
        pady=4
    )
    btn_frame.pack_propagate(False)

    # ── Left accent indicator ────────────────────────────────────
    accent = tk.Frame(
        btn_frame,
        bg=accent_color,
        width=4
    )
    accent.pack(
        side="left",
        fill="y"
    )

    # ── Content area ─────────────────────────────────────────────
    inner = tk.Frame(
        btn_frame,
        bg=normal_bg,
        padx=12,
        pady=9
    )
    inner.pack(
        side="left",
        fill="both",
        expand=True
    )

    # Main label
    lbl_main = tk.Label(
        inner,
        text=label,
        font=fonts["ui_b"],
        bg=normal_bg,
        fg="#F2F7FC",
        anchor="w",
        cursor="hand2",
    )
    lbl_main.pack(fill="x")

    # Sub label
    lbl_sub = tk.Label(
        inner,
        text=sublabel,
        font=tkfont.Font(
            family="Segoe UI",
            size=8
        ),
        bg=normal_bg,
        fg="#7891A8",
        anchor="w",
        cursor="hand2",
    )
    lbl_sub.pack(
        fill="x",
        pady=(2, 0)
    )

    # ── Small colored status dot ─────────────────────────────────
    dot = tk.Label(
        btn_frame,
        text="●",
        font=tkfont.Font(
            family="Segoe UI",
            size=7
        ),
        bg=normal_bg,
        fg=accent_color,
        cursor="hand2",
    )
    dot.pack(
        side="right",
        padx=(0, 12)
    )

    widgets = [
        btn_frame,
        inner,
        lbl_main,
        lbl_sub,
        dot,
    ]

    def _enter(event=None):
        for widget in widgets:
            widget.config(bg=hover_bg)

        accent.config(bg=accent_color)

        lbl_main.config(
            fg="#FFFFFF"
        )

        lbl_sub.config(
            fg="#9DB4C9"
        )

    def _leave(event=None):
        for widget in widgets:
            widget.config(bg=normal_bg)

        accent.config(bg=accent_color)

        lbl_main.config(
            fg="#F2F7FC"
        )

        lbl_sub.config(
            fg="#7891A8"
        )

    def _press(event=None):
        for widget in widgets:
            widget.config(bg=pressed_bg)

        accent.config(
            bg=accent_color
        )

    def _release(event=None):
        for widget in widgets:
            widget.config(bg=hover_bg)

        accent.config(
            bg=accent_color
        )

        if cmd:
            cmd()

    # Bind everything except accent bar
    for widget in widgets:
        widget.bind("<Enter>", _enter)
        widget.bind("<Leave>", _leave)
        widget.bind("<ButtonPress-1>", _press)
        widget.bind("<ButtonRelease-1>", _release)


def _status_block(parent: tk.Frame, fonts: dict) -> None:
    """Modern device connection status."""

    blk = tk.Frame(
        parent,
        bg=T["sidebar_dark"],
        pady=13,
        padx=14
    )
    blk.pack(fill="x")

    tk.Label(
        blk,
        text="DEVICE STATUS",
        font=tkfont.Font(
            family="Segoe UI",
            size=8,
            weight="bold"
        ),
        bg=T["sidebar_dark"],
        fg="#6B87A3",
    ).pack(anchor="w")

    row = tk.Frame(
        blk,
        bg=T["sidebar_dark"]
    )
    row.pack(
        anchor="w",
        pady=(9, 0)
    )

    tk.Label(
        row,
        text="●",
        font=tkfont.Font(size=10),
        bg=T["sidebar_dark"],
        fg=T["led_red"]
    ).pack(side="left")

    tk.Label(
        row,
        text="  Not Connected",
        font=tkfont.Font(
            family="Segoe UI",
            size=9
        ),
        bg=T["sidebar_dark"],
        fg=T["sidebar_text"]
    ).pack(side="left")


def _brand_block(parent: tk.Frame, fonts: dict) -> None:
    """Bottom company branding."""

    brand = tk.Frame(
        parent,
        bg=T["sidebar_dark"],
        pady=14
    )
    brand.pack(fill="x")

    tk.Frame(
        brand,
        bg=T["accent_teal"],
        height=1
    ).pack(
        fill="x",
        pady=(0, 10)
    )

    tk.Label(
        brand,
        text="SARAYU INFOTECH",
        font=tkfont.Font(
            family="Segoe UI",
            size=8,
            weight="bold"
        ),
        bg=T["sidebar_dark"],
        fg="#6B87A3",
    ).pack()

    tk.Label(
        brand,
        text="SOLUTIONS PVT LTD",
        font=tkfont.Font(
            family="Segoe UI",
            size=8
        ),
        bg=T["sidebar_dark"],
        fg="#465E76",
    ).pack()

