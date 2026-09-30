"""
toolbar.py — VMS 3000  •  Professional toolbar
Dark-title-strip + light icon band.  Groups separated by hairline rules.
"""

import tkinter as tk
from theme  import T
from icons  import IconPainter
from tooltip import ToolTip
import sys
import os

# Add src to path for UI components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from ui.connection_dialog import ConnectionDialog
from ui.com_port_detector import get_available_com_ports

# Global variables for button handlers
_root_window = None
_command_callbacks = {}

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
        ("settings", "Preferences"),
        ("connection", "Connection"),
        ("help",     "Help              (F1)"),
    ],
]


def build_toolbar(root, fonts, rack_addr_var: tk.StringVar, command_callbacks=None):
    icons = IconPainter(T["toolbar_bg"])
    
    # Store references for button handlers
    global _root_window, _command_callbacks
    _root_window = root
    _command_callbacks = command_callbacks or {}

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
        
        # Handle button click based on key
        _handle_button_click(key, btn, parent)

    btn.bind("<Enter>",            _enter)
    btn.bind("<Leave>",            _leave)
    btn.bind("<ButtonPress-1>",    _press)
    btn.bind("<ButtonRelease-1>",  _release)

    ToolTip(btn, tip)
    return btn


def _handle_button_click(key, button, parent):
    """Handle toolbar button clicks."""
    global _command_callbacks
    
    # Special handling for connection button
    if key == "connection":
        _show_connection_menu(button, parent)
        return
    
    # Check if there's a callback registered for this action
    if key in _command_callbacks:
        try:
            _command_callbacks[key]()
        except Exception as e:
            print(f"Error executing callback for {key}: {e}")
    else:
        # Default behavior for unregistered buttons
        print(f"{key} clicked (no callback registered)")
        
        # Show appropriate message based on button
        if key == "new":
            print("New file action")
        elif key == "open":
            print("Open file action")
        elif key == "save":
            print("Save file action")
        elif key == "print":
            print("Print action")
        elif key == "settings":
            print("Settings action")
        elif key == "cut":
            print("Cut action")
        elif key == "copy":
            print("Copy action")
        elif key == "paste":
            print("Paste action")
        elif key == "upload":
            print("Upload action")
        elif key == "download":
            print("Download action")
        elif key == "refresh":
            print("Refresh action")
        elif key == "help":
            print("Help action")


def _show_connection_menu(button, parent):
    """Show connection dropdown menu."""
    menu = tk.Menu(parent, tearoff=0)
    menu.add_command(label="Direct connect", command=lambda: _on_direct_connect(parent))
    menu.add_command(label="Network connect", command=lambda: _on_network_connect(parent))
    menu.add_separator()
    menu.add_command(label="Disconnect", command=lambda: _on_disconnect(parent))
    
    # Position menu below the button using the parent window
    try:
        # Try to get button position
        button.update_idletasks()
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
    except Exception:
        # Fallback to parent window position
        try:
            parent.update_idletasks()
            x = parent.winfo_rootx() + 200
            y = parent.winfo_rooty() + 100
        except Exception:
            # Ultimate fallback
            x = 100
            y = 100
    
    menu.post(x, y)


def _on_direct_connect(parent):
    """Open direct connection dialog."""
    try:
        com_ports = get_available_com_ports()
        dialog = ConnectionDialog(parent, com_ports)
        result = dialog.show()
        if result:
            print(f"Direct connect: {result}")
    except Exception as e:
        print(f"Error opening direct connect dialog: {e}")


def _on_network_connect(parent):
    """Handle network connect."""
    print("Network connect clicked")
    # TODO: Implement network connect functionality


def _on_disconnect(parent):
    """Handle disconnect."""
    print("Disconnect clicked")
    # TODO: Implement disconnect functionality