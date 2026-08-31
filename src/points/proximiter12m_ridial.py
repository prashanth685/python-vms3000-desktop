"""
proximity_monitor_3000_config.py — VMS 3000
Proximity Monitor 3000 Configuration Dialog (Proximeter I/O Module)

Exact visual match to the reference screenshot:
  - pale steel-blue window background
  - dark navy titlebar
  - flat sunken display fields for SLOT / RACK TYPE / CONFIGURATION ID
  - classic raised, beveled buttons (Ok, Options, Copy, arrows, etc.)
  - "Channel Pair Type" combobox shown with the blue highlighted
    selection look ("Radial Vibration"), matching the screenshot
  - bold blue-navy italic "VMS 3000" logo, bottom right
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from points.channel_configuration import ChannelConfigurationDialog


# ══════════════════════════════════════════════════════════════════════════
#  PALETTE — colours matched from the reference screenshot
# ══════════════════════════════════════════════════════════════════════════

C = {
    "win_bg":          "#f0f0f0",   # pale grey dialog background (matches Channel-N Configuration)
    "titlebar":        "#1a3a5c",   # navy titlebar (matches Channel-N Configuration)
    "titlebar_text":   "#ffffff",
    "close_bg":        "#c0392b",

    "group_bg":        "#f0f0f0",
    "group_border":    "#8a8f98",
    "group_label":     "#000000",

    "field_bg":        "#eef1f5",   # SLOT / RACK TYPE / CONFIG ID display box
    "field_border":    "#6b7280",

    "combo_white_bg":  "#ffffff",   # Slot I/O Module Type dropdown
    "combo_white_fg":  "#1a3a8c",

    "combo_sel_bg":    "#1a3a5c",   # highlighted "Radial Vibration" look (navy, from Channel-N titlebar)
    "combo_sel_fg":    "#ffffff",

    "btn_face":        "#e7e9ec",
    "btn_hover":       "#f2f4f6",
    "btn_press":       "#cfd4da",
    "btn_border":      "#5a5a5a",
    "btn_disabled_fg": "#8895a6",

    "text":            "#000000",
    "text_dim":        "#4a5568",

    "vms_logo":        "#17408a",
}

FONT_NAME = "Segoe UI"


class ProximityMonitor3000ConfigDialog:
    """Configuration dialog for a Proximeter I/O Module (VMS 3000 DIS_MODULE)."""

    # ------------------------------------------------------------------ #
    #  Init — slot_num is the 2nd positional arg, fonts is optional/safe  #
    # ------------------------------------------------------------------ #

    def __init__(self, parent, slot_num=6, fonts=None,
                 rack_type="VMM/12T/DISP", config_id=""):
        self._parent    = parent
        self._slot_num  = slot_num
        self._fonts     = fonts if isinstance(fonts, dict) else {}
        self._rack_type = rack_type
        self._config_id = config_id
        self._dialog    = None

    def _f(self, key, family=FONT_NAME, size=9, weight="normal", slant="roman"):
        if not isinstance(self._fonts, dict):
            self._fonts = {}
        font = self._fonts.get(key)
        if font is None:
            font = tkfont.Font(family=family, size=size, weight=weight, slant=slant)
            self._fonts[key] = font
        return font

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def show(self):
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title("Proximity Monitor 3000 Configuration")
        self._dialog.configure(bg=C["win_bg"])
        self._dialog.resizable(False, False)
        self._dialog.transient(self._parent)
        self._dialog.grab_set()

        self._style_ttk()

        self._create_titlebar()

        body = tk.Frame(self._dialog, bg=C["win_bg"], padx=14, pady=10)
        body.pack(fill="both", expand=True)

        self._create_identity_row(body)

        pairs_row = tk.Frame(body, bg=C["win_bg"])
        pairs_row.pack(fill="both", expand=True, pady=(10, 0))
        pairs_row.columnconfigure(0, weight=1)
        pairs_row.columnconfigure(1, weight=1)

        self._build_channel_pair_group(
            pairs_row, "Channel Pair 1 and 2", "Channel 1", "Channel 2", 1, 2
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self._build_channel_pair_group(
            pairs_row, "Channel Pair 3 and 4", "Channel 3", "Channel 4", 3, 4
        ).grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._create_buttons(body)

        self._dialog.update_idletasks()
        w = max(960, self._dialog.winfo_reqwidth())
        h = self._dialog.winfo_reqheight()
        sw = self._dialog.winfo_screenwidth()
        sh = self._dialog.winfo_screenheight()
        self._dialog.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ------------------------------------------------------------------ #
    #  ttk styling                                                         #
    # ------------------------------------------------------------------ #

    def _style_ttk(self):
        style = ttk.Style(self._dialog)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Plain white combobox — used for "Slot Input / Output Module Type"
        style.configure(
            "White.TCombobox",
            fieldbackground=C["combo_white_bg"],
            background=C["btn_face"],
            foreground=C["combo_white_fg"],
            arrowcolor=C["text"],
            bordercolor=C["field_border"],
            lightcolor=C["combo_white_bg"],
            darkcolor=C["field_border"],
            padding=3,
        )
        style.map("White.TCombobox",
                  fieldbackground=[("readonly", C["combo_white_bg"])],
                  foreground=[("readonly", C["combo_white_fg"])])

        # Blue "selected" combobox — used for "Channel Pair Type"
        style.configure(
            "Selected.TCombobox",
            fieldbackground=C["combo_sel_bg"],
            background=C["btn_face"],
            foreground=C["combo_sel_fg"],
            arrowcolor=C["text"],
            bordercolor=C["field_border"],
            lightcolor=C["combo_sel_bg"],
            darkcolor=C["field_border"],
            padding=3,
        )
        style.map("Selected.TCombobox",
                  fieldbackground=[("readonly", C["combo_sel_bg"])],
                  foreground=[("readonly", C["combo_sel_fg"])])

    # ------------------------------------------------------------------ #
    #  Titlebar                                                            #
    # ------------------------------------------------------------------ #

    def _create_titlebar(self):
        bar = tk.Frame(self._dialog, bg=C["titlebar"], height=26)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar, text="  Proximity Monitor 3000 Configuration",
            font=self._f("title", size=10, weight="bold"),
            bg=C["titlebar"], fg=C["titlebar_text"], anchor="w",
        ).pack(side="left", fill="both", expand=True)

        tk.Button(
            bar, text="\u2715", font=self._f("close", size=8),
            bg=C["close_bg"], fg="#ffffff", bd=1, relief="raised",
            width=3, command=self._on_cancel,
        ).pack(side="right", padx=4, pady=3)

    # ------------------------------------------------------------------ #
    #  Group-box helper                                                    #
    # ------------------------------------------------------------------ #

    def _group(self, parent, title):
        return tk.LabelFrame(
            parent, text=f" {title} ",
            font=self._f("group", size=9, weight="bold"),
            bg=C["group_bg"], fg=C["group_label"],
            bd=1, relief="groove",
            highlightbackground=C["group_border"],
            padx=10, pady=8,
        )

    # ------------------------------------------------------------------ #
    #  Identity row                                                        #
    # ------------------------------------------------------------------ #

    def _create_identity_row(self, parent):
        row = tk.Frame(parent, bg=C["win_bg"])
        row.pack(fill="x")

        left = tk.Frame(row, bg=C["win_bg"])
        left.pack(side="left", anchor="n")

        self._display_field(left, "SLOT:", str(self._slot_num), width=5, col=0)
        self._display_field(left, "RACK TYPE:", self._rack_type, width=14, col=1)
        self._display_field(left, "CONFIGURATION ID:", self._config_id, width=14, col=2)

        right = self._group(row, "Slot Input / Output Module Type")
        right.pack(side="right", fill="x", expand=True, padx=(30, 0))

        combo = ttk.Combobox(
            right, values=["Proximeter I/O Module"],
            font=self._f("field", size=9), state="readonly",
            style="White.TCombobox",
        )
        combo.set("Proximeter I/O Module")
        combo.pack(fill="x", padx=2, pady=2)

    def _display_field(self, parent, label_text, value, width, col):
        """Flat sunken display box (SLOT / RACK TYPE / CONFIGURATION ID)."""
        cell = tk.Frame(parent, bg=C["win_bg"])
        cell.grid(row=0, column=col, padx=(0, 16), sticky="w")

        tk.Label(
            cell, text=label_text, bg=C["win_bg"], fg=C["text"],
            font=self._f("label_b", size=9, weight="bold"),
        ).pack(anchor="w")

        box = tk.Label(
            cell, text=value, bg=C["field_bg"], fg=C["text"],
            font=self._f("field", size=9),
            width=width, anchor="w",
            relief="sunken", bd=2,
            highlightthickness=1, highlightbackground=C["field_border"],
            padx=4, pady=2,
        )
        box.pack(anchor="w", pady=(2, 0))

    # ------------------------------------------------------------------ #
    #  Channel Pair group                                                  #
    # ------------------------------------------------------------------ #

    def _build_channel_pair_group(self, parent, title, ch_a_name, ch_b_name,
                                   ch_a_num, ch_b_num):
        group = self._group(parent, title)

        type_row = tk.Frame(group, bg=C["win_bg"])
        type_row.pack(fill="x", pady=(0, 6))
        tk.Label(
            type_row, text="Channel Pair Type", bg=C["win_bg"], fg=C["text"],
            font=self._f("label_b", size=9, weight="bold"),
        ).pack(anchor="e")

        pair_type_combo = ttk.Combobox(
            type_row,
            values=["Radial Vibration", "Axial Vibration", "Thrust Position", "Not Used"],
            font=self._f("field", size=9), state="readonly",
            style="Selected.TCombobox",
        )
        pair_type_combo.set("Radial Vibration")
        pair_type_combo.pack(fill="x")

        body = tk.Frame(group, bg=C["win_bg"])
        body.pack(fill="both", expand=True, pady=(4, 4))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(2, weight=1)

        self._build_channel_box(body, ch_a_name, ch_a_num).grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        mid = tk.Frame(body, bg=C["win_bg"])
        mid.grid(row=0, column=1, sticky="n")
        self._raised_btn(mid, "\u21d2", None, width=3).pack(pady=(28, 4))
        self._raised_btn(mid, "Copy", None, width=8).pack(pady=4)
        self._raised_btn(mid, "\u21d0", None, width=3, enabled=False).pack(pady=(4, 0))

        self._build_channel_box(body, ch_b_name, ch_b_num).grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        arrows_row = tk.Frame(group, bg=C["win_bg"])
        arrows_row.pack(pady=(2, 0))
        self._raised_btn(arrows_row, "\u21d2", None, width=3).pack(pady=2)
        self._raised_btn(arrows_row, "\u21d0", None, width=3, enabled=False).pack(pady=2)

        return group

    def _build_channel_box(self, parent, name, channel_num):
        box = self._group(parent, name)

        var = tk.BooleanVar(value=True)

        chk = tk.Checkbutton(
            box, text="Active", variable=var,
            bg=C["win_bg"], fg=C["text"],
            activebackground=C["win_bg"], activeforeground=C["text"],
            selectcolor="#ffffff",
            font=self._f("field", size=9),
        )
        chk.pack(anchor="w", pady=(0, 8))

        options_btn = self._raised_btn(
            box, "Options",
            lambda: self._on_options(channel_num, var),
            width=10
        )
        options_btn.pack(pady=(0, 4))

        def _apply_active_state(*_):
            """Grey out the whole channel box (title, checkbox label,
            Options button) when Active is unchecked — matches the
            reference screenshot's disabled 'Channel 1' look exactly."""
            active = var.get()
            state = "normal" if active else "disabled"
            color = C["text"] if active else C["btn_disabled_fg"]
            box.config(fg=color)
            chk.config(fg=color, state="normal")  # checkbox itself stays clickable
            options_btn.config(
                state=state,
                cursor="hand2" if active else "arrow",
            )

        var.trace_add("write", _apply_active_state)
        _apply_active_state()

        return box

    # ------------------------------------------------------------------ #
    #  Classic raised, beveled button                                      #
    # ------------------------------------------------------------------ #

    def _raised_btn(self, parent, text, cmd, width=None, enabled=True):
        b = tk.Button(
            parent, text=text, command=cmd,
            font=self._f("field", size=9),
            bg=C["btn_face"], fg=C["text"],
            activebackground=C["btn_press"], activeforeground=C["text"],
            disabledforeground=C["btn_disabled_fg"],
            relief="raised", bd=2,
            highlightthickness=1, highlightbackground=C["btn_border"],
            width=width, state="normal" if enabled else "disabled",
            cursor="hand2" if enabled else "arrow",
        )
        b.bind("<Enter>", lambda e: b.config(bg=C["btn_hover"]) if str(b["state"]) == "normal" else None)
        b.bind("<Leave>", lambda e: b.config(bg=C["btn_face"]))
        return b

    # ------------------------------------------------------------------ #
    #  Bottom button bar                                                   #
    # ------------------------------------------------------------------ #

    def _create_buttons(self, parent):
        bar = tk.Frame(parent, bg=C["win_bg"])
        bar.pack(fill="x", pady=(12, 0))

        left = tk.Frame(bar, bg=C["win_bg"])
        left.pack(side="left")
        self._raised_btn(left, "Ok", self._on_ok, width=10).pack(side="left")
        self._raised_btn(left, "Set defaults", self._on_set_defaults, width=12).pack(side="left", padx=(8, 0))
        self._raised_btn(left, "Cancel", self._on_cancel, width=10).pack(side="left", padx=(8, 0))

        mid = tk.Frame(bar, bg=C["win_bg"])
        mid.pack(side="left", padx=(60, 0))
        self._raised_btn(mid, "Print", self._on_print, width=10).pack(side="left")
        self._raised_btn(mid, "Help", self._on_help, width=10).pack(side="left", padx=(8, 0))

        tk.Label(
            bar, text="VMS 3000",
            font=self._f("logo", family="Segoe UI", size=15, weight="bold", slant="italic"),
            bg=C["win_bg"], fg=C["vms_logo"],
        ).pack(side="right")

    # ------------------------------------------------------------------ #
    #  Handlers                                                            #
    # ------------------------------------------------------------------ #

    def _on_options(self, channel_num, active_var=None):
        """
        Open the Channel-N Configuration dialog (exact match to the
        Channel-1 .. Channel-4 reference screenshots) for the given
        channel, pre-filled with this module's slot and rack type.
        """
        dialog = ChannelConfigurationDialog(
            self._dialog,
            channel_num,
            slot_num=self._slot_num,
            fonts=self._fonts,
            rack_type=self._rack_type,
            active=active_var.get() if active_var is not None else True,
        )
        dialog.show()

    def _on_ok(self):
        print("OK pressed")
        self._dialog.destroy()

    def _on_set_defaults(self):
        print("Set defaults pressed")

    def _on_cancel(self):
        self._dialog.destroy()

    def _on_print(self):
        print("Print pressed")

    def _on_help(self):
        print("Help pressed")


# ══════════════════════════════════════════════════════════════════════
#  Standalone preview
# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    dlg = ProximityMonitor3000ConfigDialog(root, 6)   # (parent, slot_num)
    dlg.show()
    root.mainloop()