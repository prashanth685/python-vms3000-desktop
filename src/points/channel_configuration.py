"""
channel_configuration.py — VMS 3000
Channel-N Configuration Dialog

Exact visual + functional match to the reference "Channel-1 Configuration" /
"Channel-2 Configuration" screenshots:
  - CHANNEL / 'ACTIVE' / SLOT / RACK TYPE identity row
  - a real two-tab switcher: "Transducer setup" and "Variables + Alarms".
    Clicking a tab RAISES that tab's panel to the front (tk.Frame.tkraise
    on two frames stacked in the same grid cell) — an instant content
    swap, exactly like a classic Windows tab control. It is NOT a
    "card"-style flip/slide animation.
  - "Variables + Alarm" panel, pixel-matched to the screenshots:
      Enable — Full Scale Range / Clamp Value for Direct & Gap rows
      Zero Position (Gap) — spinner + "Adjust" button
      Alert Latching / Danger Latching checkboxes
      Delay — Alert / Danger spinners with range hints
      Trip Multiply — spinner with range hint
      Recorder Output — dropdown
  - classic raised, beveled buttons (Ok, Set defaults, Cancel, Print, Help)
  - bold blue-navy italic "VMS 3000" logo, bottom right

NOTE: the "Transducer setup" tab's fields are not visible in either
reference screenshot (both were captured with "Variables + Alarms"
selected). The fields below are a reasonable placeholder for a proximity
transducer setup screen — swap in the real fields/labels whenever they're
available.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont


# ══════════════════════════════════════════════════════════════════════════
#  PALETTE — kept consistent with proximiter12m_ridial.py / sixm_option.py
# ══════════════════════════════════════════════════════════════════════════

C = {
    "win_bg":          "#f0f0f0",
    "titlebar":        "#1a3a5c",
    "titlebar_text":   "#ffffff",
    "close_bg":        "#c0392b",

    "group_bg":        "#f0f0f0",
    "group_border":    "#8a8f98",
    "group_label":     "#000000",

    "field_bg":        "#eef1f5",
    "field_border":    "#6b7280",

    "combo_white_bg":  "#ffffff",
    "combo_white_fg":  "#1a3a8c",

    "btn_face":        "#e7e9ec",
    "btn_hover":       "#f2f4f6",
    "btn_press":       "#cfd4da",
    "btn_border":      "#5a5a5a",
    "btn_disabled_fg": "#8895a6",

    "tab_sel_bg":      "#f0f0f0",   # selected tab blends into the panel
    "tab_unsel_bg":    "#d7dbe0",   # unselected tab sits slightly "behind"
    "tab_border":      "#8a8f98",

    "text":            "#000000",
    "text_dim":        "#4a5568",

    "vms_logo":        "#17408a",
}

FONT_NAME = "Segoe UI"


class ChannelConfigurationDialog:
    """Channel-N Configuration dialog (Transducer setup / Variables + Alarms)."""

    # ------------------------------------------------------------------ #
    #  Init                                                                #
    # ------------------------------------------------------------------ #

    def __init__(self, parent, channel_num, slot_num=6, fonts=None,
                 rack_type="", active=True, on_ok=None):
        self._parent      = parent
        self._channel_num = channel_num
        self._slot_num     = slot_num
        self._fonts        = fonts if isinstance(fonts, dict) else {}
        self._rack_type    = rack_type
        self._active       = active
        self._dialog        = None
        self._on_ok_callback = on_ok

        self._tabs         = {}   # name -> content frame
        self._tab_buttons   = {}  # name -> tab button widget
        self._active_tab   = None

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
        self._dialog.title(f"Channel-{self._channel_num} Configuration")
        self._dialog.configure(bg=C["win_bg"])
        self._dialog.resizable(False, False)
        self._dialog.transient(self._parent)
        self._dialog.grab_set()

        self._style_ttk()

        self._create_titlebar()

        body = tk.Frame(self._dialog, bg=C["win_bg"], padx=14, pady=10)
        body.pack(fill="both", expand=True)

        self._create_identity_row(body)

        self._create_tab_strip(body)
        self._create_tab_panels(body)

        self._create_buttons(body)

        self._select_tab("Variables + Alarms")

        self._dialog.update_idletasks()
        w = self._dialog.winfo_reqwidth()
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

        style.configure(
            "White.TCombobox",
            fieldbackground=C["combo_white_bg"],
            background=C["btn_face"],
            foreground=C["combo_white_fg"],
            arrowcolor=C["text"],
            bordercolor=C["field_border"],
            lightcolor=C["combo_white_bg"],
            darkcolor=C["field_border"],
            padding=2,
        )
        style.map("White.TCombobox",
                  fieldbackground=[("readonly", C["combo_white_bg"])],
                  foreground=[("readonly", C["combo_white_fg"])])

    # ------------------------------------------------------------------ #
    #  Titlebar                                                            #
    # ------------------------------------------------------------------ #

    def _create_titlebar(self):
        bar = tk.Frame(self._dialog, bg=C["titlebar"], height=26)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar, text=f"  Channel-{self._channel_num} Configuration",
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
    #  Identity row — CHANNEL / 'ACTIVE' / SLOT / RACK TYPE                #
    # ------------------------------------------------------------------ #

    def _create_identity_row(self, parent):
        row = tk.Frame(parent, bg=C["win_bg"])
        row.pack(fill="x", pady=(0, 8))

        tk.Label(
            row, text="CHANNEL", bg=C["win_bg"], fg=C["text"],
            font=self._f("label_b", size=9, weight="bold"),
        ).pack(side="left")

        tk.Label(
            row, text=str(self._channel_num), bg=C["field_bg"], fg=C["text"],
            font=self._f("field", size=9, weight="bold"),
            width=3, relief="sunken", bd=2,
            highlightthickness=1, highlightbackground=C["field_border"],
        ).pack(side="left", padx=(6, 10))

        status = "'ACTIVE'" if self._active else "'INACTIVE'"
        tk.Label(
            row, text=status, bg=C["field_bg"], fg=C["text"],
            font=self._f("field", size=9, weight="bold"),
            width=10, relief="sunken", bd=2,
            highlightthickness=1, highlightbackground=C["field_border"],
        ).pack(side="left", padx=(0, 30))

        tk.Label(
            row, text="SLOT", bg=C["win_bg"], fg=C["text"],
            font=self._f("label_b", size=9, weight="bold"),
        ).pack(side="left")

        tk.Label(
            row, text=str(self._slot_num), bg=C["field_bg"], fg=C["text"],
            font=self._f("field", size=9),
            width=6, relief="sunken", bd=2,
            highlightthickness=1, highlightbackground=C["field_border"],
        ).pack(side="left", padx=(6, 30))

        tk.Label(
            row, text="RACK TYPE", bg=C["win_bg"], fg=C["text"],
            font=self._f("label_b", size=9, weight="bold"),
        ).pack(side="left")

        tk.Label(
            row, text=self._rack_type, bg=C["field_bg"], fg=C["text"],
            font=self._f("field", size=9),
            width=16, anchor="w", relief="sunken", bd=2,
            highlightthickness=1, highlightbackground=C["field_border"],
        ).pack(side="left", padx=(6, 0))

    # ------------------------------------------------------------------ #
    #  Tab strip — real switching, not a "card"                          #
    # ------------------------------------------------------------------ #

    def _create_tab_strip(self, parent):
        strip = tk.Frame(parent, bg=C["win_bg"])
        strip.pack(fill="x")

        for name in ("Transducer setup", "Variables + Alarms"):
            btn = tk.Label(
                strip, text=name,
                font=self._f("tab", size=9, weight="normal"),
                bg=C["tab_unsel_bg"], fg=C["text"],
                bd=1, relief="raised",
                padx=10, pady=4, cursor="hand2",
            )
            btn.pack(side="left", padx=(0, 2))
            btn.bind("<Button-1>", lambda e, n=name: self._select_tab(n))
            self._tab_buttons[name] = btn

    def _create_tab_panels(self, parent):
        # Both panels occupy the SAME grid cell; selecting a tab just
        # raises the corresponding frame to the front — an immediate
        # switch, no transition/animation.
        container = tk.Frame(parent, bg=C["win_bg"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        transducer = tk.Frame(container, bg=C["win_bg"])
        transducer.grid(row=0, column=0, sticky="nsew")
        self._build_transducer_setup_tab(transducer)
        self._tabs["Transducer setup"] = transducer

        variables = tk.Frame(container, bg=C["win_bg"])
        variables.grid(row=0, column=0, sticky="nsew")
        self._build_variables_alarms_tab(variables)
        self._tabs["Variables + Alarms"] = variables

    def _select_tab(self, name):
        """Switch the visible tab panel. This is a plain raise/lower —
        the exact same mechanism as clicking a tab in any standard
        Windows tab control, not a stylised card transition."""
        if self._active_tab == name:
            return
        self._active_tab = name

        for tab_name, btn in self._tab_buttons.items():
            selected = (tab_name == name)
            btn.config(
                bg=C["tab_sel_bg"] if selected else C["tab_unsel_bg"],
                font=self._f("tab", size=9, weight="bold" if selected else "normal"),
                relief="solid" if selected else "raised",
            )

        self._tabs[name].tkraise()

    # ------------------------------------------------------------------ #
    #  "Variables + Alarms" tab — pixel-matched to the reference           #
    # ------------------------------------------------------------------ #

    def _build_variables_alarms_tab(self, parent):
        panel = self._group(parent, "Variables + Alarm")
        panel.pack(fill="both", expand=True, pady=(0, 8))

        top = tk.Frame(panel, bg=C["win_bg"])
        top.pack(fill="x")

        # ---- Enable: Full Scale Range / Clamp Value for Direct & Gap ----
        enable = self._group(top, "Enable")
        enable.pack(side="left", fill="both", expand=True, padx=(0, 10))

        hdr = tk.Frame(enable, bg=C["win_bg"])
        hdr.grid(row=0, column=0, columnspan=3, sticky="w")
        tk.Label(hdr, text="", bg=C["win_bg"], width=7).pack(side="left")
        tk.Label(
            hdr, text="Full Scale Range", bg=C["win_bg"], fg=C["text"],
            font=self._f("label_b", size=9, weight="bold"),
        ).pack(side="left", padx=(24, 40))
        tk.Label(
            hdr, text="Clamp Value", bg=C["win_bg"], fg=C["text"],
            font=self._f("label_b", size=9, weight="bold"),
        ).pack(side="left")

        direct_scale_values = [
            "0-10 mil pp", "0-15 mil pp", "0-20 mil pp", "0-100 mil pp",
            "0-150 \u00b5m pp", "0-200 \u00b5m pp", "0-400 \u00b5m pp", "0-500 \u00b5m pp",
        ]
        # Gap "full scale range" on this module is a DC bias-voltage
        # range rather than a mil/µm span — not shown fully in the
        # screenshot beyond "-24Vdc", so a plausible preset list is used.
        gap_scale_values = ["-24Vdc", "-20Vdc", "-18Vdc", "-16Vdc", "-12Vdc", "-10Vdc", "-8Vdc"]

        self._direct_row = self._build_enable_row(
            enable, row=1, label="Direct",
            scale_values=direct_scale_values, scale_default="0-10 mil pp",
            clamp_default="0",
        )
        self._gap_row = self._build_enable_row(
            enable, row=2, label="Gap",
            scale_values=gap_scale_values, scale_default="-24Vdc",
            clamp_default="0",
        )

        # ---- Zero Position (Gap) ----
        zero = self._group(top, "Zero Position")
        zero.pack(side="left", fill="both", padx=(0, 0))

        zrow = tk.Frame(zero, bg=C["win_bg"])
        zrow.pack(fill="x", pady=(2, 8))
        tk.Label(
            zrow, text="Zero Position\n(Gap)", bg=C["win_bg"], fg=C["text"],
            font=self._f("field", size=9), justify="left",
        ).pack(side="left")

        zspin = self._spinbox(zrow, value="-9.75", width=6)
        zspin.pack(side="left", padx=(8, 4))
        tk.Label(
            zrow, text="Volts", bg=C["win_bg"], fg=C["text"],
            font=self._f("field", size=9),
        ).pack(side="left")

        self._raised_btn(zero, "Adjust", None, width=12, enabled=False).pack(pady=(0, 2))

        # ---- Alert Latching / Danger Latching ----
        latch_row = tk.Frame(panel, bg=C["win_bg"])
        latch_row.pack(fill="x", pady=(8, 4))

        tk.Checkbutton(
            latch_row, text="Alert Latching",
            bg=C["win_bg"], fg=C["text"], activebackground=C["win_bg"],
            font=self._f("field", size=9),
        ).pack(side="left")

        tk.Checkbutton(
            latch_row, text="Danger Latching",
            bg=C["win_bg"], fg=C["text"], activebackground=C["win_bg"],
            font=self._f("field", size=9),
        ).pack(side="left", padx=(30, 0))

        # ---- Delay / Trip Multiply ----
        mid = tk.Frame(panel, bg=C["win_bg"])
        mid.pack(fill="x", pady=(4, 4))

        delay = self._group(mid, "Delay")
        delay.pack(side="left", fill="both", expand=True, padx=(0, 10))

        alert_row = tk.Frame(delay, bg=C["win_bg"])
        alert_row.pack(fill="x", pady=(0, 6))
        tk.Label(alert_row, text="Alert", bg=C["win_bg"], fg=C["text"],
                 font=self._f("field", size=9), width=7, anchor="w").pack(side="left")
        self._spinbox(alert_row, value="3", width=4).pack(side="left", padx=(0, 6))
        tk.Label(alert_row, text="1 - 60 s", bg=C["win_bg"], fg=C["text"],
                 font=self._f("field", size=9)).pack(side="left")

        danger_row = tk.Frame(delay, bg=C["win_bg"])
        danger_row.pack(fill="x")
        tk.Label(danger_row, text="Danger", bg=C["win_bg"], fg=C["text"],
                 font=self._f("field", size=9), width=7, anchor="w").pack(side="left")
        self._spinbox(danger_row, value="1", width=4).pack(side="left", padx=(0, 6))
        tk.Label(danger_row, text="1.0 - 60.0", bg=C["win_bg"], fg=C["text"],
                 font=self._f("field", size=9)).pack(side="left")

        trip = self._group(mid, "Trip Multiply")
        trip.pack(side="left", fill="both")

        trip_row = tk.Frame(trip, bg=C["win_bg"])
        trip_row.pack(fill="x")
        self._spinbox(trip_row, value="1", width=4).pack(side="left", padx=(0, 6))
        tk.Label(
            trip_row, text="1 to 3 (Step of\n0.25)", bg=C["win_bg"], fg=C["text"],
            font=self._f("field", size=9), justify="left",
        ).pack(side="left")

        # ---- Recorder Output ----
        rec = self._group(panel, "Recorder Output")
        rec.pack(fill="x", pady=(4, 0))

        rec_combo = ttk.Combobox(
            rec, values=["NONE", "Recorder 1", "Recorder 2"],
            font=self._f("field", size=9), state="readonly",
            style="White.TCombobox", width=20,
        )
        rec_combo.set("NONE")
        rec_combo.pack(anchor="w", padx=2, pady=2)

    def _build_enable_row(self, parent, row, label, scale_values, scale_default, clamp_default):
        tk.Label(
            parent, text=label, bg=C["win_bg"], fg=C["text"],
            font=self._f("field", size=9), width=7, anchor="w",
        ).grid(row=row, column=0, sticky="w", pady=4)

        scale_combo = ttk.Combobox(
            parent, values=scale_values, font=self._f("field", size=9),
            state="readonly", style="White.TCombobox", width=14,
        )
        scale_combo.set(scale_default)
        scale_combo.grid(row=row, column=1, sticky="w", padx=(0, 30), pady=4)

        clamp_spin = self._spinbox(parent, value=clamp_default, width=5)
        clamp_spin.grid(row=row, column=2, sticky="w", pady=4)

        return scale_combo, clamp_spin

    # ------------------------------------------------------------------ #
    #  "Transducer setup" tab — placeholder (not shown in screenshots)    #
    # ------------------------------------------------------------------ #

    def _build_transducer_setup_tab(self, parent):
        panel = self._group(parent, "Transducer Setup")
        panel.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(
            panel,
            text=("Transducer setup fields were not visible in the reference\n"
                  "screenshots (both were captured on the Variables + Alarms tab).\n"
                  "Placeholder fields are shown below — replace with the real\n"
                  "labels/values whenever available."),
            bg=C["win_bg"], fg=C["text_dim"],
            font=self._f("field", size=8, slant="italic"),
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(panel, bg=C["win_bg"])
        grid.pack(fill="x")

        def _row(r, label, values, default):
            tk.Label(
                grid, text=label, bg=C["win_bg"], fg=C["text"],
                font=self._f("field", size=9), width=20, anchor="w",
            ).grid(row=r, column=0, sticky="w", pady=4)
            combo = ttk.Combobox(
                grid, values=values, font=self._f("field", size=9),
                state="readonly", style="White.TCombobox", width=20,
            )
            combo.set(default)
            combo.grid(row=r, column=1, sticky="w", pady=4)
            return combo

        _row(0, "Transducer Type", ["Standard Proximitor", "Reverse Mount", "Extended Range"], "Standard Proximitor")
        _row(1, "Probe Type", ["5 mm", "8 mm", "11 mm"], "8 mm")
        _row(2, "Extension Cable Length", ["1 m", "3 m", "5 m", "9 m"], "5 m")
        _row(3, "Sensitivity", ["100 mV/mil", "200 mV/mil", "7.87 mV/\u00b5m"], "200 mV/mil")

    # ------------------------------------------------------------------ #
    #  Small spinbox helper (Clamp Value / Zero Position / Delay / etc.)  #
    # ------------------------------------------------------------------ #

    def _spinbox(self, parent, value, width=5, frm=-999, to=999):
        sb = tk.Spinbox(
            parent, from_=frm, to=to, width=width,
            font=self._f("field", size=9),
            bg=C["field_bg"], fg=C["text"],
            relief="sunken", bd=2,
            highlightthickness=1, highlightbackground=C["field_border"],
            buttonbackground=C["btn_face"],
        )
        sb.delete(0, "end")
        sb.insert(0, value)
        return sb

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
        bar.pack(fill="x", pady=(4, 0))

        left = tk.Frame(bar, bg=C["win_bg"])
        left.pack(side="left")
        self._raised_btn(left, "Ok", self._on_ok, width=10).pack(side="left")
        self._raised_btn(left, "Set defaults", self._on_set_defaults, width=12).pack(side="left", padx=(8, 0))
        self._raised_btn(left, "Cancel", self._on_cancel, width=10).pack(side="left", padx=(8, 0))

        mid = tk.Frame(bar, bg=C["win_bg"])
        mid.pack(side="left", padx=(40, 0))
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

    def _on_ok(self):
        print("OK pressed")
        if self._on_ok_callback:
            self._on_ok_callback(self._channel_num)
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

    dlg = ChannelConfigurationDialog(root, 1, slot_num=10, rack_type="", active=True)
    dlg.show()
    root.mainloop()