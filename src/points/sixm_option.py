"""
sixm_option.py — VMS 3000  •  3000/6M Options Configuration Dialog

Exact visual match to the "Proximity Monitor 3000 Configuration" reference
screenshot, adapted for the 3000/6M module's 2 channels instead of 4:
  - pale steel-grey window background
  - dark navy titlebar with red close button
  - flat, thin-bordered white display fields for SLOT / RACK TYPE /
    CONFIGURATION ID (no group-box borders anywhere — every section
    header is a plain bold label sitting above its control, exactly
    like the screenshot)
  - "Slot Input / Output Module Type" — bold label + plain white dropdown,
    no surrounding border box
  - "Channel Pair Type" — bold label right-aligned above a full-width,
    solid navy combobox bar with white text ("Radial Vibration")
  - Channel boxes (Channel 1 / Channel 2) — bold label above a thin
    rectangular border containing an "Active" checkbox and an "Options"
    button
  - classic raised, beveled buttons (Ok, Options, Copy, arrows, etc.)
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
    "win_bg":          "#f0f0f0",   # pale grey dialog background
    "titlebar":        "#1a3a5c",   # navy titlebar
    "titlebar_text":   "#ffffff",
    "close_bg":        "#c0392b",

    "group_label":     "#000000",

    "field_bg":        "#ffffff",   # SLOT / RACK TYPE / CONFIG ID display box
    "field_border":    "#8a8f98",

    "box_bg":          "#f0f0f0",   # Channel N thin-border box background
    "box_border":      "#8a8f98",

    "combo_white_bg":  "#ffffff",   # Slot I/O Module Type dropdown
    "combo_white_fg":  "#1a3a8c",

    "combo_sel_bg":    "#1a3a5c",   # full-width navy "Channel Pair Type" bar
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


class SixMOptionsDialog:
    """Configuration dialog for a 3000/6M Module (VMS 3000) — pixel-matched
    to the reference "Proximity Monitor 3000 Configuration" screenshot,
    scaled down to 2 channels."""

    # ------------------------------------------------------------------ #
    #  Init — slot_num is the 2nd positional arg, fonts is optional/safe  #
    # ------------------------------------------------------------------ #

    def __init__(self, parent, slot_num=6, fonts=None,
                 rack_type="VMM/6M/DISP", config_id=""):
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
        self._dialog.title("3000/6M Options Configuration")
        self._dialog.configure(bg=C["win_bg"])
        self._dialog.resizable(False, False)
        self._dialog.transient(self._parent)
        self._dialog.grab_set()

        self._style_ttk()

        self._create_titlebar()

        body = tk.Frame(self._dialog, bg=C["win_bg"], padx=14, pady=10)
        body.pack(fill="both", expand=True)

        self._create_identity_row(body)

        pair_row = tk.Frame(body, bg=C["win_bg"])
        pair_row.pack(fill="both", expand=True, pady=(14, 0))
        pair_row.columnconfigure(0, weight=1)
        pair_row.columnconfigure(2, weight=1)

        self._build_channel_pair_group(
            pair_row, "Channel Pair 1 and 2", "Channel 1", "Channel 2", 1, 2
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Frame(pair_row, bg=C["box_border"], width=1).grid(row=0, column=1, sticky="ns")

        self._build_channel_pair_group(
            pair_row, "Channel Pair 3 and 4", "Channel 3", "Channel 4", 3, 4
        ).grid(row=0, column=2, sticky="nsew", padx=(10, 0))

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
            "White6M.TCombobox",
            fieldbackground=C["combo_white_bg"],
            background=C["btn_face"],
            foreground=C["combo_white_fg"],
            arrowcolor=C["text"],
            bordercolor=C["field_border"],
            lightcolor=C["combo_white_bg"],
            darkcolor=C["field_border"],
            padding=3,
        )
        style.map("White6M.TCombobox",
                  fieldbackground=[("readonly", C["combo_white_bg"])],
                  foreground=[("readonly", C["combo_white_fg"])])

        # Solid navy "Channel Pair Type" bar — full width, highlighted look
        style.configure(
            "Selected6M.TCombobox",
            fieldbackground=C["combo_sel_bg"],
            background=C["combo_sel_bg"],
            foreground=C["combo_sel_fg"],
            arrowcolor=C["combo_sel_fg"],
            bordercolor=C["field_border"],
            lightcolor=C["combo_sel_bg"],
            darkcolor=C["combo_sel_bg"],
            padding=4,
        )
        style.map("Selected6M.TCombobox",
                  fieldbackground=[("readonly", C["combo_sel_bg"])],
                  foreground=[("readonly", C["combo_sel_fg"])],
                  arrowcolor=[("readonly", C["combo_sel_fg"])])

    # ------------------------------------------------------------------ #
    #  Titlebar                                                            #
    # ------------------------------------------------------------------ #

    def _create_titlebar(self):
        bar = tk.Frame(self._dialog, bg=C["titlebar"], height=26)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar, text="  3000/6M Options Configuration",
            font=self._f("title", size=11, weight="bold"),
            bg=C["titlebar"], fg=C["titlebar_text"], anchor="w",
        ).pack(side="left", fill="both", expand=True)

        tk.Button(
            bar, text="\u2715", font=self._f("close", size=8),
            bg=C["close_bg"], fg="#ffffff", bd=1, relief="raised",
            width=3, command=self._on_cancel,
        ).pack(side="right", padx=4, pady=3)

    # ------------------------------------------------------------------ #
    #  Section header helper — bold plain label, NOT a group-box border    #
    # ------------------------------------------------------------------ #

    def _section_label(self, parent, title, anchor="w"):
        return tk.Label(
            parent, text=title,
            font=self._f("label_b", size=9, weight="bold"),
            bg=C["win_bg"], fg=C["group_label"], anchor=anchor,
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

        right = tk.Frame(row, bg=C["win_bg"])
        right.pack(side="right", fill="x", expand=True, padx=(30, 0))

        self._section_label(right, "Slot Input / Output Module Type").pack(anchor="w")

        combo = ttk.Combobox(
            right, values=["3000/6M Module"],
            font=self._f("field", size=9), state="readonly",
            style="White6M.TCombobox",
        )
        combo.set("3000/6M Module")
        combo.pack(fill="x", padx=2, pady=(2, 0))

    def _display_field(self, parent, label_text, value, width, col):
        """Flat, thin-bordered white display box (SLOT / RACK TYPE /
        CONFIGURATION ID) — matches the reference exactly."""
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
            relief="solid", bd=1,
            padx=4, pady=3,
        )
        box.pack(anchor="w", pady=(2, 0))

    # ------------------------------------------------------------------ #
    #  Channel Pair group                                                  #
    # ------------------------------------------------------------------ #

    def _build_channel_pair_group(self, parent, title, ch_a_name, ch_b_name,
                                   ch_a_num, ch_b_num):
        group = tk.Frame(parent, bg=C["win_bg"])

        # Header row: pair title (left) + "Channel Pair Type" (right)
        header = tk.Frame(group, bg=C["win_bg"])
        header.pack(fill="x")
        self._section_label(header, title).pack(side="left")
        self._section_label(header, "Channel Pair Type", anchor="e").pack(side="right")

        # Full-width solid-navy combobox bar
        pair_type_combo = ttk.Combobox(
            group,
            values=["Radial Vibration", "Axial Vibration", "Thrust Position", "Not Used"],
            font=self._f("field", size=9), state="readonly",
            style="Selected6M.TCombobox",
        )
        pair_type_combo.set("Radial Vibration")
        pair_type_combo.pack(fill="x", pady=(2, 6))

        body = tk.Frame(group, bg=C["win_bg"])
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(2, weight=1)

        self._build_channel_box(body, ch_a_name, ch_a_num).grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        mid = tk.Frame(body, bg=C["win_bg"])
        mid.grid(row=0, column=1, sticky="n")
        self._raised_btn(mid, "\u21d2", None, width=3, enabled=False).pack(pady=(28, 4))
        self._raised_btn(mid, "Copy", None, width=8).pack(pady=4)
        self._raised_btn(mid, "\u21d0", None, width=3, enabled=False).pack(pady=(4, 0))

        self._build_channel_box(body, ch_b_name, ch_b_num).grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        arrows_row = tk.Frame(group, bg=C["win_bg"])
        arrows_row.pack(pady=(6, 0))
        self._raised_btn(arrows_row, "\u21d2", None, width=3, enabled=False).pack(pady=2)
        self._raised_btn(arrows_row, "\u21d0", None, width=3, enabled=False).pack(pady=2)

        return group

    def _build_channel_box(self, parent, name, channel_num):
        """Bold label above a thin rectangular border — matches the
        reference's "Channel 1" / "Channel 2" boxes exactly (label sits
        outside the border, not baked into it)."""
        wrap = tk.Frame(parent, bg=C["win_bg"])

        self._section_label(wrap, name).pack(anchor="w", pady=(0, 4))

        box = tk.Frame(
            wrap, bg=C["box_bg"],
            highlightthickness=1, highlightbackground=C["box_border"],
            bd=0,
        )
        box.pack(fill="both", expand=True)

        inner = tk.Frame(box, bg=C["box_bg"], padx=10, pady=10)
        inner.pack(fill="both", expand=True)

        name_label = wrap.winfo_children()[0]

        var = tk.BooleanVar(value=True)

        chk = tk.Checkbutton(
            inner, text="Active", variable=var,
            bg=C["box_bg"], fg=C["text"],
            activebackground=C["box_bg"], activeforeground=C["text"],
            selectcolor="#ffffff",
            font=self._f("field", size=9),
        )
        chk.pack(anchor="w", pady=(0, 8))

        options_btn = self._raised_btn(
            inner, "Options",
            lambda: self._on_options(channel_num, var),
            width=10
        )
        options_btn.pack(anchor="w")

        def _apply_active_state(*_):
            """Grey out the whole channel box (title, checkbox label,
            Options button) when Active is unchecked — matches the
            reference screenshot's disabled 'Channel 1' look exactly."""
            active = var.get()
            state = "normal" if active else "disabled"
            color = C["text"] if active else C["btn_disabled_fg"]
            name_label.config(fg=color)
            chk.config(fg=color, state="normal")  # checkbox itself stays clickable
            options_btn.config(
                state=state,
                cursor="hand2" if active else "arrow",
            )

        var.trace_add("write", _apply_active_state)
        _apply_active_state()

        return wrap

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

    dlg = SixMOptionsDialog(root, 6)   # (parent, slot_num)
    dlg.show()
    root.mainloop()