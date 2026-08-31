"""
rack_setup.py — VMS 3000  •  Rack Setup dialog
Card-type design matching Configuration Settings popup.
Navy titlebar with VMS 3000 badge, teal accent rule, grouped option panels,
and button strip with status bar background.

Usage from main.py:

    import rack_setup

    def open_rack_setup():
        rack_setup.open_rack_setup(root, on_ok=handle_rack_config)

    commands = {
        "rack_setup": open_rack_setup,
        ...
    }

    def handle_rack_config(cfg: dict):
        # cfg = {"system_type": "ch20", "rack_size": "full",
        #        "interface": "standard"}
        print(cfg)
"""

import tkinter as tk
import tkinter.font as tkfont

try:
    from theme import T
except ImportError:
    T = {}

# ── Fallback palette (used only if a key is missing from theme.T) ──────
_DEFAULTS = {
    "win_bg":           "#f5f7fa",
    "titlebar":         "#1a3a5c",
    "accent":           "#1a4fa0",
    "accent_light":     "#3a6fcc",
    "accent_teal":      "#0891b2",
    "btn_face":         "#e4e9f0",
    "btn_hover":        "#d0e4f8",
    "btn_border":       "#b4bfcc",
    "text":             "#1a2533",
    "text_dim":         "#5a6a7a",
    "text_white":       "#ffffff",
    "status_bg":        "#dde3ec",
    "status_border":    "#b4bfcc",
    "led_amber":        "#f59e0b",
}


def _c(key: str) -> str:
    return T.get(key, _DEFAULTS[key])


_SYSTEM_TYPES = [
    ("standard",         "Standard"),
    ("standard_display",  "Standard With Local Display"),
    ("ch20",              "20 Channel With Local Display And Relay"),
]

_RACK_SIZES = [
    ("full", "Full Rack [12 Slots]"),
    ("mini", "Mini Rack [6 Slots]"),
]

_INTERFACES = [
    ("standard", "Standard Rack Interface Module"),
    ("ethernet", "Ethernet Interface Module"),
]

# System types that lock the rack to Full Rack / Standard Interface only.
_LOCKED_TYPES = {"ch20"}


def open_rack_setup(parent, fonts: dict = None, on_ok=None, on_cancel=None,
                     initial: dict = None):
    """Show the Rack Setup dialog. Returns the Toplevel instance."""
    fonts = fonts or {}
    initial = initial or {"system_type": "ch20", "rack_size": "full",
                           "interface": "standard"}

    f_title = fonts.get("ui_b") or tkfont.Font(family="Segoe UI", size=10, weight="bold")
    f_group = tkfont.Font(family="Segoe UI", size=9, weight="bold")
    f_item  = fonts.get("ui") or tkfont.Font(family="Segoe UI", size=9)
    f_btn   = tkfont.Font(family="Segoe UI", size=9, weight="bold")

    win = tk.Toplevel(parent)
    win.title("Rack Setup")
    win.configure(bg=_c("win_bg"))
    win.geometry("420x500")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    # ── Titlebar strip (navy) ──────────────────────────────────────
    bar = tk.Frame(win, bg=_c("titlebar"), pady=10)
    bar.pack(fill="x")

    # Left: dialog title in white bold
    tk.Label(
        bar,
        text="  Rack Setup",
        font=f_title,
        bg=_c("titlebar"),
        fg=_c("text_white"),
        anchor="w",
    ).pack(side="left", fill="x", expand=True)

    # Right: VMS 3000 badge
    badge = tk.Label(
        bar,
        text="  VMS 3000  ",
        font=f_title,
        bg=_c("accent_light"),
        fg=_c("text_white"),
        relief="flat",
        padx=6,
        pady=4,
    )
    badge.pack(side="right", padx=(0, 12))

    # ── Teal accent rule under titlebar ───────────────────────────
    tk.Frame(win, bg=_c("accent_teal"), height=3).pack(fill="x")

    # ── Body ──────────────────────────────────────────────────────
    body = tk.Frame(win, bg=_c("win_bg"), padx=16, pady=12)
    body.pack(fill="both", expand=True)

    system_var = tk.StringVar(value=initial.get("system_type", "ch20"))
    rack_var = tk.StringVar(value=initial.get("rack_size", "full"))
    iface_var = tk.StringVar(value=initial.get("interface", "standard"))

    def _group(label):
        grp = tk.LabelFrame(body, text=f"  {label}  ", font=f_group,
                             bg=_c("win_bg"), fg=_c("accent"),
                             bd=2, relief="groove", padx=14, pady=10)
        grp.pack(fill="x", pady=(0, 10))
        return grp

    def _radio(grp, var, value, text):
        rb = tk.Radiobutton(
            grp, text=text, variable=var, value=value,
            font=f_item, bg=_c("win_bg"), fg=_c("text"),
            activebackground=_c("win_bg"), selectcolor="#ffffff",
            anchor="w", disabledforeground=_c("text_dim"),
        )
        rb.pack(fill="x", anchor="w", pady=2)
        return rb

    # System Type
    grp_sys = _group("System Type")
    for value, text in _SYSTEM_TYPES:
        _radio(grp_sys, system_var, value, text)

    # Rack Size
    grp_rack = _group("Rack Size")
    rack_widgets = {}
    for value, text in _RACK_SIZES:
        rack_widgets[value] = _radio(grp_rack, rack_var, value, text)

    # Interface Module
    grp_iface = _group("Interface Module")
    iface_widgets = {}
    for value, text in _INTERFACES:
        iface_widgets[value] = _radio(grp_iface, iface_var, value, text)

    # ── Dependency logic: 20-channel type locks rack size + interface ──
    def _apply_lock(*_a):
        locked = system_var.get() in _LOCKED_TYPES
        if locked:
            rack_var.set("full")
            iface_var.set("standard")
            rack_widgets["mini"].config(state="disabled")
            iface_widgets["ethernet"].config(state="disabled")
        else:
            rack_widgets["mini"].config(state="normal")
            iface_widgets["ethernet"].config(state="normal")

    system_var.trace_add("write", _apply_lock)
    _apply_lock()

    # ── Button strip ──────────────────────────────────────────────
    strip = tk.Frame(win, bg=_c("status_bg"), pady=12, relief="flat", bd=0)
    tk.Frame(win, bg=_c("status_border"), height=1).pack(fill="x")
    strip.pack(fill="x", padx=0)

    inner = tk.Frame(strip, bg=_c("status_bg"))
    inner.pack(padx=16)

    def _btn(text, cmd, style="normal"):
        if style == "primary":
            bg  = _c("accent")
            fg  = _c("text_white")
            abg = _c("accent_light")
            afg = _c("text_white")
        else:
            bg  = _c("btn_face")
            fg  = _c("text")
            abg = _c("btn_hover")
            afg = _c("text")

        b = tk.Button(
            inner,
            text=f"  {text}  ",
            command=cmd,
            font=f_btn,
            bg=bg,
            fg=fg,
            activebackground=abg,
            activeforeground=afg,
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=_c("btn_border"),
        )
        b.pack(side="left", padx=(0, 8))

        def _e(ev): b.config(bg=abg, fg=afg)
        def _l(ev): b.config(bg=bg,  fg=fg)
        b.bind("<Enter>", _e)
        b.bind("<Leave>", _l)
        return b

    def _close():
        if on_cancel:
            on_cancel()
        win.destroy()

    def _ok():
        cfg = {
            "system_type": system_var.get(),
            "rack_size": rack_var.get(),
            "interface": iface_var.get(),
        }
        if on_ok:
            on_ok(cfg)
        win.destroy()

    _btn("Ok", _ok, style="primary")
    _btn("Cancel", _close, style="normal")

    # ── Size & centre ─────────────────────────────────────────────
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - 420) // 2
    y = (sh - 500) // 2
    win.geometry(f"+{x}+{y}")

    win.bind("<Escape>", _close)
    return win


# ── Standalone test ─────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    root.title("VMS 3000 (test host)")

    def _show():
        open_rack_setup(root, on_ok=lambda cfg: print("Saved:", cfg))

    tk.Button(root, text="Open Rack Setup", command=_show).pack(pady=40)
    root.mainloop()