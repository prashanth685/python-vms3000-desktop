"""
monitors.py — VMS 3000  •  Cascading Menu System
Cascading menu for module selection: Monitors → Proximeter/Tachometer → Models
"""

import tkinter as tk
import tkinter.font as tkfont


# ══════════════════════════════════════════════════════════════════════════════
#  THEME  —  VMS 3000 Industrial SCADA colour palette
# ══════════════════════════════════════════════════════════════════════════════

T = {
    # ── Window & chrome ──────────────────────────────────────────────
    "win_bg":           "#f5f7fa",
    "titlebar":         "#1a3a5c",

    # ── Buttons ───────────────────────────────────────────────────────
    "btn_face":         "#e4e9f0",
    "btn_hover":        "#d0e4f8",
    "btn_border":       "#b4bfcc",

    # ── Text ──────────────────────────────────────────────────────────
    "text":             "#1a2533",
    "text_white":       "#ffffff",
    "text_dim":         "#6b7280",

    # ── Status bar ────────────────────────────────────────────────────
    "status_bg":        "#dde3ec",
    "status_border":    "#b4bfcc",

    # ── Accent ────────────────────────────────────────────────────────
    "accent":           "#1a4fa0",
    "accent_light":     "#3a6fcc",
    "accent_teal":      "#0891b2",
}


# ══════════════════════════════════════════════════════════════════════════════
#  CASCADING MENU CLASS  —  matches the reference flyout design exactly
# ══════════════════════════════════════════════════════════════════════════════

class CascadingMenu:
    """
    Native OS-style cascading (flyout) menu for module selection.

    Structure (top → bottom, left → right):
      Level 1: Monitors, Gateways, Relay, No Modules
      Level 2 (Monitors): Proximeter Monitor, Tachometer Monitor
      Level 3 (Proximeter): 3000/12M/DIS, 3000/6M
      Level 3 (Tachometer): 3000/12M/TAC, 3000/6M/TAC
      Level 2 (Relay): 3000/RLY
    """

    def __init__(self, parent, fonts, on_selection):
        """
        Initialize cascading menu.

        Args:
            parent: Parent widget
            fonts: Font dictionary
            on_selection: Callback function when a selection is made
        """
        self._parent = parent
        self._fonts = fonts
        self._on_selection = on_selection
        self._menus = {}  # Store menu references
        self._current_selection = None

    def _f(self, key, family="Segoe UI", size=9, weight="normal"):
        """Font helper."""
        return self._fonts.get(key, tkfont.Font(family=family, size=size, weight=weight))

    def _new_menu(self, parent_menu):
        """Create a themed tk.Menu bound to the given parent menu."""
        return tk.Menu(
            parent_menu,
            tearoff=0,
            bg=T["win_bg"],
            fg=T["text"],
            activebackground=T["accent_light"],
            activeforeground=T["text_white"],
            font=self._f("sm", size=9),
        )

    def show_menu(self, x, y):
        """Show the main cascading menu at the given screen coordinates."""
        main_menu = self._new_menu(self._parent)

        # Monitors ▸ (Proximeter Monitor ▸ / Tachometer Monitor ▸)
        self._add_monitors_submenu(main_menu)
        main_menu.add_separator()

        # Gateways
        main_menu.add_command(label="Gateways",
                               command=lambda: self._on_selection("Gateways"))
        main_menu.add_separator()

        # Relay ▸
        self._add_relay_submenu(main_menu)
        main_menu.add_separator()

        # No Modules
        main_menu.add_command(label="No Modules",
                               command=lambda: self._on_selection("No Modules"))

        # Show menu at position
        main_menu.tk_popup(x, y)

    def _add_monitors_submenu(self, parent_menu):
        """Add Monitors submenu with cascading options."""
        monitors_menu = self._new_menu(parent_menu)

        # Add Proximeter Monitor with its own submenu
        self._add_proximeter_submenu(monitors_menu)

        # Add Tachometer Monitor with its own submenu
        tachometer_menu = self._new_menu(monitors_menu)
        tachometer_menu.add_command(label="3000/12M/TAC",
                                     command=lambda: self._on_selection("3000/12M/TAC"))
        tachometer_menu.add_command(label="3000/6M/TAC",
                                     command=lambda: self._on_selection("3000/6M/TAC"))

        monitors_menu.add_cascade(label="Tachometer Monitor", menu=tachometer_menu)

        parent_menu.add_cascade(label="Monitors", menu=monitors_menu)

    def _add_proximeter_submenu(self, parent_menu):
        """Add Proximeter Monitor submenu with model options."""
        proximeter_menu = self._new_menu(parent_menu)

        proximeter_menu.add_command(label="3000/12M/DIS",
                                     command=lambda: self._on_selection("3000/12M/DIS"))
        proximeter_menu.add_command(label="3000/6M",
                                     command=lambda: self._on_selection("3000/6M"))

        parent_menu.add_cascade(label="Proximeter Monitor", menu=proximeter_menu)

    def _add_relay_submenu(self, parent_menu):
        """Add Relay submenu with model options."""
        relay_menu = self._new_menu(parent_menu)

        relay_menu.add_command(label="3000/RLY",
                                command=lambda: self._on_selection("3000/RLY"))

        parent_menu.add_cascade(label="Relay", menu=relay_menu)


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone preview
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x200")

    fonts = {
        "ui_b": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "sm":   tkfont.Font(family="Segoe UI", size=9),
        "sm_b": tkfont.Font(family="Segoe UI", size=9,  weight="bold"),
        "mono": tkfont.Font(family="Consolas", size=10),
    }

    def on_selection(selection):
        print(f"Selected: {selection}")

    def show(event):
        menu = CascadingMenu(root, fonts, on_selection)
        menu.show_menu(event.x_root, event.y_root)

    tk.Label(root, text="Right-click anywhere", bg="white").pack(fill="both", expand=True)
    root.bind("<Button-1>", show)

    root.mainloop()