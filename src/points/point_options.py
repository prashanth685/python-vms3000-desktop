"""
point_options.py — VMS 3000  •  Point Options Context Menu
Theme-matched to the industrial SCADA palette (navy/steel/amber/teal).
Provides right-click context menu for DIS_MODULE with Setpoints and Point Names options.
"""

import tkinter as tk
import tkinter.font as tkfont


# ══════════════════════════════════════════════════════════════════════════════
#  THEME  —  VMS 3000 Industrial SCADA colour palette
# ══════════════════════════════════════════════════════════════════════════════

T = {
    # ── Context menu ───────────────────────────────────────────────────────
    "menu_bg":          "#ffffff",
    "menu_fg":          "#1a2533",
    "menu_active_bg":   "#e4edf9",
    "menu_active_fg":   "#1a2533",
    "menu_border":      "#c9d3e0",
    "menu_sep":         "#d7dbe0",
    
    # ── Text ──────────────────────────────────────────────────────────────
    "text":             "#1a2533",
    "text_dim":         "#5a6a7a",
    "text_white":       "#ffffff",
    
    # ── Accent ────────────────────────────────────────────────────────────
    "accent":           "#1a4fa0",
    "accent_light":     "#3a6fcc",
}


# ══════════════════════════════════════════════════════════════════════════════
#  Point Options Context Menu
# ══════════════════════════════════════════════════════════════════════════════

class PointOptionsContextMenu:
    """Right-click context menu for DIS_MODULE with Setpoints and Point Names options."""
    
    def __init__(self, parent, fonts, slot_num, on_options=None, on_setpoints=None, on_point_names=None):
        """
        Initialize the context menu.
        
        Args:
            parent: Parent widget (usually canvas)
            fonts: Font dictionary from main application
            slot_num: Slot number for the DIS_MODULE
            on_options: Callback when Options is selected
            on_setpoints: Callback when Setpoints is selected
            on_point_names: Callback when Point Names is selected
        """
        self._parent = parent
        self._fonts = fonts
        self._slot_num = slot_num
        self._on_options = on_options
        self._on_setpoints = on_setpoints
        self._on_point_names = on_point_names
        
        self._menu = tk.Menu(
            parent,
            bg=T["menu_bg"],
            fg=T["menu_fg"],
            activebackground=T["menu_active_bg"],
            activeforeground=T["menu_active_fg"],
            borderwidth=1,
            relief="solid",
            tearoff=0
        )
        
        self._build_menu()
    
    def _build_menu(self):
        """Build the context menu items based on available callbacks."""
        item_count = 0

        # Options option
        if self._on_options:
            self._menu.add_command(
                label="Options...",
                font=self._fonts.get("normal", tkfont.Font(family="Segoe UI", size=9)),
                command=self._on_options_click
            )
            item_count += 1

        # Separator if we have options and will have more items
        if self._on_options and (self._on_setpoints or self._on_point_names):
            self._menu.add_separator(background=T["menu_sep"])

        # Setpoints option
        if self._on_setpoints:
            self._menu.add_command(
                label="Setpoints...",
                font=self._fonts.get("normal", tkfont.Font(family="Segoe UI", size=9)),
                command=self._on_setpoints_click
            )
            item_count += 1

        # Separator if we have setpoints and point names
        if self._on_setpoints and self._on_point_names:
            self._menu.add_separator(background=T["menu_sep"])

        # Point Names option
        if self._on_point_names:
            self._menu.add_command(
                label="Point Names...",
                font=self._fonts.get("normal", tkfont.Font(family="Segoe UI", size=9)),
                command=self._on_point_names_click
            )
            item_count += 1
    
    def _on_options_click(self):
        """Handle Options menu item click."""
        if self._on_options:
            self._on_options(self._slot_num)
    
    def _on_setpoints_click(self):
        """Handle Setpoints menu item click."""
        if self._on_setpoints:
            self._on_setpoints(self._slot_num)
    
    def _on_point_names_click(self):
        """Handle Point Names menu item click."""
        if self._on_point_names:
            self._on_point_names(self._slot_num)
    
    def show(self, x, y):
        """Display the context menu at the specified coordinates."""
        self._menu.tk_popup(x, y)
    
    def destroy(self):
        """Destroy the menu."""
        self._menu.destroy()