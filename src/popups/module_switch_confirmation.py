"""
module_switch_confirmation.py — VMS 3000  •  Generic Module Switch Confirmation Popup
Confirmation dialog when switching between any modules
"""

import tkinter as tk
import tkinter.font as tkfont


# ══════════════════════════════════════════════════════════════════════════════
#  THEME  —  VMS 3000 Industrial SCADA colour palette
# ══════════════════════════════════════════════════════════════════════════════

T = {
    # ── Window & chrome ──────────────────────────────────────────────
    "win_bg":           "#eef1f4",
    "titlebar":         "#1d5fa8",

    # ── Buttons ───────────────────────────────────────────────────────
    "btn_face":         "#e7e9ec",
    "btn_hover":        "#f2f4f6",
    "btn_border":       "#5a5a5a",

    # ── Text ──────────────────────────────────────────────────────────
    "text":             "#1a1a1a",
    "text_white":       "#ffffff",
    "text_dim":         "#9a9a9a",

    # ── Accent ────────────────────────────────────────────────────────
    "accent":           "#1d5fa8",
    "accent_light":     "#2f7dc4",
    "accent_teal":      "#0891b2",
}


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIRMATION POPUP CLASS
# ══════════════════════════════════════════════════════════════════════════════

class ModuleSwitchConfirmationPopup:
    """
    Generic confirmation popup when switching between any modules.
    
    Shows a message asking if the user wants to switch from current module to target module.
    """

    def __init__(self, parent, fonts, current_module, target_module, on_confirm):
        """
        Initialize confirmation popup.
        
        Args:
            parent: Parent widget
            fonts: Font dictionary
            current_module: Current module name (e.g., "3000/12M/DIS")
            target_module: Target module name (e.g., "3000/6M")
            on_confirm: Callback function when confirmed (True) or cancelled (False)
        """
        self._fonts = fonts
        self._parent = parent
        self._current_module = current_module
        self._target_module = target_module
        self._on_confirm = on_confirm
        self._dialog = None
        self._confirmed = False

        self._create_dialog()

    def _f(self, key, family="Segoe UI", size=9, weight="normal"):
        """Font helper."""
        return self._fonts.get(key, tkfont.Font(family=family, size=size, weight=weight))

    def _create_dialog(self):
        """Create the confirmation dialog."""
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title("Module Switch Confirmation")
        self._dialog.configure(bg=T["win_bg"])
        self._dialog.resizable(False, False)
        self._dialog.grab_set()

        # ── Titlebar strip (navy) ──────────────────────────────────────
        self._create_titlebar()

        # ── Teal accent rule under titlebar ───────────────────────────
        tk.Frame(self._dialog, bg=T["accent_teal"], height=3).pack(fill="x")

        # ── Body ──────────────────────────────────────────────────────
        body = tk.Frame(self._dialog, bg=T["win_bg"], padx=20, pady=20)
        body.pack(fill="both", expand=True)

        # Message
        tk.Label(
            body,
            text=f"Do you want to switch {self._current_module} to {self._target_module}?",
            font=self._f("ui_b", size=11, weight="bold"),
            bg=T["win_bg"],
            fg=T["text"],
            wraplength=350,
            justify="center",
        ).pack(pady=(0, 10))

        tk.Label(
            body,
            text="The rest will remain the same.",
            font=self._f("sm", size=9),
            bg=T["win_bg"],
            fg=T["text_dim"],
            wraplength=350,
            justify="center",
        ).pack(pady=(0, 20))

        # Button frame
        btn_frame = tk.Frame(body, bg=T["win_bg"])
        btn_frame.pack(fill="x")

        ub = self._f("ui_b", size=10, weight="bold")

        # Yes button
        yes_btn = tk.Button(
            btn_frame,
            text="  Yes  ",
            command=self._on_yes,
            font=ub,
            bg=T["accent"],
            fg=T["text_white"],
            activebackground=T["accent_light"],
            activeforeground=T["text_white"],
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=T["btn_border"],
        )
        yes_btn.pack(side="left", padx=(0, 10))

        # Hover effects for Yes button
        def _yes_e(ev): yes_btn.config(bg=T["accent_light"])
        def _yes_l(ev): yes_btn.config(bg=T["accent"])
        yes_btn.bind("<Enter>", _yes_e)
        yes_btn.bind("<Leave>", _yes_l)

        # No button
        no_btn = tk.Button(
            btn_frame,
            text="  No  ",
            command=self._on_no,
            font=ub,
            bg=T["btn_face"],
            fg=T["text"],
            activebackground=T["btn_hover"],
            activeforeground=T["text"],
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=T["btn_border"],
        )
        no_btn.pack(side="left")

        # Hover effects for No button
        def _no_e(ev): no_btn.config(bg=T["btn_hover"])
        def _no_l(ev): no_btn.config(bg=T["btn_face"])
        no_btn.bind("<Enter>", _no_e)
        no_btn.bind("<Leave>", _no_l)

        # ── Size & centre ─────────────────────────────────────────────
        self._dialog.update_idletasks()
        w, h = 400, 200
        sw = self._dialog.winfo_screenwidth()
        sh = self._dialog.winfo_screenheight()
        self._dialog.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _create_titlebar(self):
        """Create titlebar."""
        bar = tk.Frame(self._dialog, bg=T["titlebar"], pady=10)
        bar.pack(fill="x")

        tk.Label(
            bar,
            text="  Module Switch Confirmation  ",
            font=self._f("ui_b", size=11, weight="bold"),
            bg=T["titlebar"],
            fg=T["text_white"],
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        tk.Label(
            bar,
            text="  VMS 3000  ",
            font=self._f("ui_b", size=10, weight="bold"),
            bg=T["accent_light"],
            fg=T["text_white"],
            relief="flat",
            padx=6,
            pady=4,
        ).pack(side="right", padx=(0, 12))

    def _on_yes(self):
        """Handle Yes button click."""
        self._confirmed = True
        if self._on_confirm:
            self._on_confirm(True)
        self._dialog.destroy()

    def _on_no(self):
        """Handle No button click."""
        self._confirmed = False
        if self._on_confirm:
            self._on_confirm(False)
        self._dialog.destroy()

    def show(self):
        """Display the dialog."""
        self._dialog.wait_window()
        return self._confirmed


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone preview
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    fonts = {
        "ui_b": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "sm":   tkfont.Font(family="Segoe UI", size=9),
        "sm_b": tkfont.Font(family="Segoe UI", size=9,  weight="bold"),
    }

    def on_confirm(confirmed):
        print(f"Confirmed: {confirmed}")

    popup = ModuleSwitchConfirmationPopup(
        root, fonts, "3000/12M/DIS", "3000/6M", on_confirm
    )
    result = popup.show()
    print(f"Result: {result}")
    root.destroy()
