"""
open_config_load.py — VMS 3000  •  Load Configuration File Dialog
Theme-matched to the industrial SCADA palette (navy/steel/amber/teal).
All colours, fonts, sizes and highlights come directly from T{}.
Single self-contained file — no external theme.py required.
"""

import tkinter as tk
from tkinter import filedialog
import tkinter.font as tkfont


# ══════════════════════════════════════════════════════════════════════════════
#  THEME  —  VMS 3000 Industrial SCADA colour palette
# ══════════════════════════════════════════════════════════════════════════════

T = {
    # ── Window & chrome ──────────────────────────────────────────────
    "win_bg":           "#f5f7fa",
    "titlebar":         "#1a3a5c",

    # ── Toolbar ──────────────────────────────────────────────────────
    "toolbar_bg":       "#fafbfc",
    "toolbar_border":   "#b8c4d4",
    "toolbar_sep":      "#c8d4e4",

    # ── Menubar ───────────────────────────────────────────────────────
    "menu_bg":          "#2a4a6e",
    "menu_fg":          "#e8f0ff",
    "menu_active_bg":   "#3a6a9e",
    "menu_active_fg":   "#ffffff",
    "menu_drop_bg":     "#2a5080",
    "menu_sep":         "#3a6090",

    # ── Sidebar ───────────────────────────────────────────────────────
    "sidebar_bg":       "#e8ecf0",
    "sidebar_dark":     "#d0d8e0",
    "sidebar_rule":     "#b8c4d4",
    "sidebar_btn":      "#f5f7fa",
    "sidebar_btn_h":    "#e0e8f0",
    "sidebar_btn_p":    "#c8d4e4",
    "sidebar_text":     "#3a4a5a",
    "sidebar_text_hi":  "#1a2533",

    # ── Rack shell ────────────────────────────────────────────────────
    "rack_shell_top":   "#b8c4d4",
    "rack_shell_bot":   "#a0b0c0",
    "rack_row":         "#d0d8e0",
    "rack_screw":       "#708090",

    # ── Slot cards ────────────────────────────────────────────────────
    "slot_bg":          "#d0d8e0",
    "slot_face":        "#c8d4e0",
    "slot_edge_hi":     "#e0e8f0",
    "slot_edge_sh":     "#a8b8c8",
    "slot_cap":         "#f5f7fa",
    "slot_grip":        "#c0d0e0",
    "slot_sel":         "#3a6fcc",
    "slot_sel_face":    "#4a8ae0",
    "slot_num_fg":      "#4a6a98",
    "slot_mod_fg":      "#1a2533",

    # ── PSM module ────────────────────────────────────────────────────
    "psm_body":         "#d0d8e0",
    "psm_brand":        "#1a4fa0",
    "psm_brand2":       "#0d3080",
    "psm_label":        "#2a4a68",
    "psm_3000":         "#1a4fa0",
    "psm_plate":        "#c0d0e0",
    "psm_plate_text":   "#1a4fa0",

    # ── Buttons ───────────────────────────────────────────────────────
    "btn_face":         "#e4e9f0",
    "btn_hover":        "#d0e4f8",
    "btn_press":        "#b0ccee",
    "btn_shadow":       "#8a9bb0",
    "btn_border":       "#b4bfcc",

    # ── Text ──────────────────────────────────────────────────────────
    "text":             "#1a2533",
    "text_dim":         "#5a6a7a",
    "text_hint":        "#1a5ab8",
    "text_white":       "#ffffff",

    # ── Status bar ────────────────────────────────────────────────────
    "status_bg":        "#dde3ec",
    "status_border":    "#b4bfcc",
    "status_section":   "#ccd4e0",

    # ── LEDs ──────────────────────────────────────────────────────────
    "led_green":        "#22c55e",
    "led_green_glow":   "#16a34a",
    "led_amber":        "#f59e0b",
    "led_red":          "#ef4444",
    "led_blue":         "#3b82f6",
    "led_off":          "#334155",

    # ── Accent ────────────────────────────────────────────────────────
    "accent":           "#1a4fa0",
    "accent_light":     "#3a6fcc",
    "accent_teal":      "#0891b2",
}


# ══════════════════════════════════════════════════════════════════════════════
#  POPUP CLASS
# ══════════════════════════════════════════════════════════════════════════════

class LoadConfigDialog:
    """
    Load Configuration File dialog — VMS 3000 SCADA theme.
    
    Opens a file dialog to select .rcs configuration files.
    Design matches the configuration_settings popup styling.
    """

    # ------------------------------------------------------------------ #
    #  Init                                                                #
    # ------------------------------------------------------------------ #

    def __init__(self, parent, fonts):
        self._fonts  = fonts
        self._parent = parent
        self._dialog = None
        self._selected_file = None

    # ------------------------------------------------------------------ #
    #  Font helper                                                         #
    # ------------------------------------------------------------------ #

    def _f(self, key, family="Segoe UI", size=9, weight="normal"):
        return self._fonts.get(key, tkfont.Font(family=family, size=size, weight=weight))

    # ------------------------------------------------------------------ #
    #  Show file dialog                                                    #
    # ------------------------------------------------------------------ #

    def show(self):
        """Open file dialog to select .rcs configuration file."""
        self._selected_file = filedialog.askopenfilename(
            title="VM3000 SOFTWARE FILES",
            parent=self._parent,
            filetypes=[
                ("Rack Configuration Files", "*.rcs"),
                ("All Files", "*.*")
            ],
            initialdir="C:/"
        )
        
        if self._selected_file:
            print(f"Configuration file selected: {self._selected_file}")
            # TODO: Add logic to load and parse the selected .rcs file
            return self._selected_file
        return None

    # ------------------------------------------------------------------ #
    #  Get selected file path                                              #
    # ------------------------------------------------------------------ #

    def get_selected_file(self):
        """Return the path of the selected file."""
        return self._selected_file


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone preview
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    root.title("VMS 3000 - Load Configuration Test")
    root.geometry("400x300")
    root.configure(bg=T["win_bg"])

    fonts = {
        "ui_b": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "sm":   tkfont.Font(family="Segoe UI", size=9),
        "sm_b": tkfont.Font(family="Segoe UI", size=9,  weight="bold"),
        "mono": tkfont.Font(family="Consolas", size=10),
    }

    def on_load():
        dialog = LoadConfigDialog(root, fonts)
        file_path = dialog.show()
        if file_path:
            result_label.config(text=f"Loaded: {file_path.split('/')[-1]}")
        else:
            result_label.config(text="No file selected")

    # Test button
    btn = tk.Button(
        root,
        text="Load Configuration",
        command=on_load,
        font=fonts["ui_b"],
        bg=T["accent"],
        fg=T["text_white"],
        activebackground=T["accent_light"],
        activeforeground=T["text_white"],
        relief="flat",
        bd=0,
        padx=20,
        pady=10,
        cursor="hand2",
    )
    btn.pack(pady=50)

    result_label = tk.Label(
        root,
        text="Click button to load configuration file",
        font=fonts["sm"],
        bg=T["win_bg"],
        fg=T["text"],
    )
    result_label.pack(pady=20)

    root.mainloop()
