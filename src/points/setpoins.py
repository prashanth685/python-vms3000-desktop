"""
setpoins.py — VMS 3000  •  Setpoints Configuration Dialog
"Setpoints - Radial Vibration (Slot N)"

Professional "card" UI (matches connection.py): white content cards with a
teal accent header strip, pill-style buttons, vertical thermometer gauges.

  - Alert / Alarm 1 card  -> "Direct mil pp" gauge + "Gap Vdc" gauge
  - Danger / Alarm 2 card -> mode dropdowns + "Direct mil pp" gauge
  - Channel selector, Ok / Copy / Defaults / Cancel buttons, VMS 3000 badge

IMPORTANT: this module must be saved as  points/setpoins.py  (exact filename,
including the project's spelling) since that is what rack_area.py imports:
    from points.setpoins import SetpointsDialog
Make sure there is only ONE copy of this file on the import path (check for
a stray/older copy elsewhere, e.g. a duplicated project folder) and delete
any stale points/__pycache__ directory after replacing the file.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont


# ══════════════════════════════════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════════════════════════════════

T = {
    "win_bg":        "#eef1f6",     # page background (behind cards)
    "group_border":  "#c9d3e0",
    "titlebar":      "#1a3a5c",

    "text":          "#1a2533",
    "text_dim":      "#5a6a7a",

    "card_bg":       "#ffffff",
    "card_header":   "#0f6e7d",
    "card_header_fg": "#ffffff",

    "entry_bg":      "#ffffff",
    "entry_border":  "#000000",

    "gauge_border":  "#000000",
    "gauge_track":   "#ffffff",
    "gauge_yellow":  "#f2c318",
    "gauge_green":   "#2fa22a",
    "gauge_red":     "#e21f1f",
    "gauge_tick":    "#ffffff",
    "pointer":       "#000000",
    "pointer2":      "#c8161d",

    "btn_border":       "#b4bfcc",
    "btn_primary":      "#1a4fa0",
    "btn_primary_hov":  "#2a63bd",
    "btn_primary_fg":   "#ffffff",
    "btn_outline_fg":   "#1a3a5c",
    "btn_outline_bd":   "#a9b7c8",
    "btn_outline_hov":  "#e4edf9",

    "accent_teal":   "#0891b2",
    "vms_blue":      "#0d3fa0",

    "menu_bg":       "#1a3a5c",
    "menu_fg":       "#ffffff",
    "toolbar_bg":    "#eef1f6",
    "toolbar_border": "#c9d3e0",
    "card_border":   "#c9d3e0",
}

FONT_NAME = "Segoe UI"


# ══════════════════════════════════════════════════════════════════════════
#  Shared card / button helpers (mirrors connection.py styling)
# ══════════════════════════════════════════════════════════════════════════

def make_card(parent, title, header_font):
    """White card panel with a teal accent header strip. Returns the body Frame."""
    outer = tk.Frame(parent, bg=T["group_border"])
    outer.pack(side="left", fill="both", expand=True, padx=6)

    card = tk.Frame(outer, bg=T["card_bg"])
    card.pack(fill="both", expand=True, padx=1, pady=1)

    header = tk.Frame(card, bg=T["card_header"])
    header.pack(fill="x")

    spaced_title = " ".join(list(title.upper()))
    tk.Label(
        header, text=spaced_title, font=header_font,
        bg=T["card_header"], fg=T["card_header_fg"],
        anchor="w", padx=12, pady=6,
    ).pack(fill="x")

    body = tk.Frame(card, bg=T["card_bg"], padx=10, pady=10)
    body.pack(fill="both", expand=True)
    return body


def make_pill_button(parent, text, command, font, kind="outline", enabled=True):
    """Pill-style button: kind='primary' (solid navy) or 'outline' (bordered)."""
    if kind == "primary":
        bg, fg, hov, border = T["btn_primary"], T["btn_primary_fg"], T["btn_primary_hov"], T["btn_primary"]
    else:
        bg, fg, hov, border = T["card_bg"], T["btn_outline_fg"], T["btn_outline_hov"], T["btn_outline_bd"]

    holder = tk.Frame(parent, bg=border)
    holder.pack(side="right", padx=(6, 0))

    b = tk.Button(
        holder, text=f"  {text}  ", command=command, font=font,
        bg=bg, fg=fg, activebackground=hov, activeforeground=fg,
        relief="flat", bd=0, padx=12, pady=6,
        cursor="hand2" if enabled else "arrow",
        disabledforeground="#9aa0aa",
    )
    b.pack(padx=1, pady=1)

    if not enabled:
        b.configure(state="disabled", bg="#eef1f6")
        holder.configure(bg="#c7cfda")
    else:
        b.bind("<Enter>", lambda e: b.config(bg=hov))
        b.bind("<Leave>", lambda e: b.config(bg=bg))

    return b


# ══════════════════════════════════════════════════════════════════════════
#  SetpointsDialog
# ══════════════════════════════════════════════════════════════════════════

class SetpointsDialog:
    """Setpoints - Radial Vibration configuration dialog for a DIS_MODULE channel."""

    def __init__(self, parent, fonts, slot_num):
        self._parent = parent
        self._fonts = fonts
        self._slot_num = slot_num
        self._dialog = None

        # ---- monitor selection ----
        self.monitor_selection = "3000/12M/DIS"

        # ---- live values (defaults match the reference screenshot) ----
        self.direct1_value = 3          # Alert/Alarm 1 - Direct mil pp
        self.direct1_top, self.direct1_bottom = 10, 0

        self.gap_value = -15.6          # Alert/Alarm 1 - Gap Vdc
        self.gap_top, self.gap_bottom = -24, 0
        self.gap_secondary = -8.4       # secondary threshold marker

        self.direct2_value = 6          # Danger/Alarm 2 - Direct mil pp
        self.direct2_top, self.direct2_bottom = 10, 0

        # ---- canvas references for gauge updates ----
        self._canvas_direct1 = None
        self._canvas_direct2 = None
        self._canvas_gap = None

        # ---- configurable colors ----
        self.colors = {
            "gauge_yellow": T["gauge_yellow"],
            "gauge_green": T["gauge_green"],
            "gauge_red": T["gauge_red"],
            "gauge_tick": T["gauge_tick"],
            "pointer": T["pointer"],
            "pointer2": T["pointer2"],
        }

    # ──────────────────────────────────────────────────────────────────
    def show(self):
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title(f"Setpoints -Radial Vibration (Slot {self._slot_num})")
        self._dialog.geometry("680x550")
        self._dialog.configure(bg=T["win_bg"])
        self._dialog.resizable(False, False)

        self._dialog.transient(self._parent)
        self._dialog.grab_set()

        self._f_norm  = tkfont.Font(family=FONT_NAME, size=9)
        self._f_bold  = tkfont.Font(family=FONT_NAME, size=9, weight="bold")
        self._f_small = tkfont.Font(family=FONT_NAME, size=8)
        self._f_head  = tkfont.Font(family=FONT_NAME, size=8, weight="bold")
        self._f_vms   = tkfont.Font(family=FONT_NAME, size=13, weight="bold", slant="italic")

        self._build_ui()

        self._dialog.update_idletasks()
        x = self._parent.winfo_x() + (self._parent.winfo_width() - self._dialog.winfo_width()) // 2
        y = self._parent.winfo_y() + (self._parent.winfo_height() - self._dialog.winfo_height()) // 2
        self._dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        main = tk.Frame(self._dialog, bg=T["win_bg"], padx=12, pady=12)
        main.pack(fill="both", expand=True)

        top_row = tk.Frame(main, bg=T["win_bg"])
        top_row.pack(fill="both", expand=True)

        # ═══════════════════════ Alert / Alarm 1 card ═══════════════════
        card1 = make_card(top_row, "Alert / Alarm 1", self._f_head)
        cols1 = tk.Frame(card1, bg=T["card_bg"])
        cols1.pack(fill="both", expand=True)

        # --- Direct mil pp (Alert/Alarm 1) ---
        col_direct1 = tk.Frame(cols1, bg=T["card_bg"])
        col_direct1.pack(side="left", padx=(4, 20))

        tk.Label(col_direct1, text="Direct\nmil pp", font=self._f_bold,
                  bg=T["card_bg"], fg=T["text"], justify="center").pack()

        self._entry_direct1 = self._value_box(col_direct1, self.direct1_value)
        self._entry_direct1.pack(pady=(2, 6))
        self._entry_direct1.bind("<KeyRelease>", lambda e: self._on_direct1_realtime())
        self._entry_direct1.bind("<FocusOut>", lambda e: self._on_direct1_validate())
        self._entry_direct1.bind("<Return>", lambda e: self._on_direct1_validate())

        c1 = tk.Canvas(col_direct1, width=70, height=250, bg=T["card_bg"], highlightthickness=0)
        c1.pack()
        self._canvas_direct1 = c1
        self._draw_gauge(
            c1, x=28, y=8, w=26, h=210,
            zones=[(0.00, 0.85, self.colors["gauge_yellow"]), (0.85, 1.00, self.colors["gauge_green"])],
            top_text=str(self.direct1_top), bottom_text=str(self.direct1_bottom),
            pointer_frac=self._frac(self.direct1_value, self.direct1_top, self.direct1_bottom),
        )

        self._en_direct1 = tk.BooleanVar(value=True)
        tk.Checkbutton(col_direct1, text="Enabled", variable=self._en_direct1,
                        bg=T["card_bg"], fg=T["text"], font=self._f_small,
                        activebackground=T["card_bg"]).pack(pady=(6, 0))

        # --- Gap Vdc (Alert/Alarm 1) ---
        col_gap = tk.Frame(cols1, bg=T["card_bg"])
        col_gap.pack(side="left")

        tk.Label(col_gap, text="Gap\nVdc", font=self._f_bold,
                  bg=T["card_bg"], fg=T["text"], justify="center").pack()

        self._entry_gap = self._value_box(col_gap, self.gap_value)
        self._entry_gap.pack(pady=(2, 6))
        self._entry_gap.bind("<KeyRelease>", lambda e: self._on_gap_realtime())
        self._entry_gap.bind("<FocusOut>", lambda e: self._on_gap_validate())
        self._entry_gap.bind("<Return>", lambda e: self._on_gap_validate())

        c2 = tk.Canvas(col_gap, width=70, height=250, bg=T["card_bg"], highlightthickness=0)
        c2.pack()
        self._canvas_gap = c2
        self._draw_gauge(
            c2, x=28, y=8, w=26, h=210,
            zones=[(0.00, 0.12, self.colors["gauge_yellow"]),
                   (0.12, 0.62, self.colors["gauge_green"]),
                   (0.62, 1.00, self.colors["gauge_yellow"])],
            top_text=str(self.gap_top), bottom_text=str(self.gap_bottom),
            pointer_frac=self._frac(self.gap_value, self.gap_top, self.gap_bottom),
            pointer2_frac=self._frac(self.gap_secondary, self.gap_top, self.gap_bottom),
        )

        self._gap_secondary_box = self._value_box(col_gap, self.gap_secondary, small=True)
        self._gap_secondary_box.pack(pady=(4, 0))
        self._gap_secondary_box.bind("<KeyRelease>", lambda e: self._on_gap_secondary_realtime())
        self._gap_secondary_box.bind("<FocusOut>", lambda e: self._on_gap_secondary_validate())
        self._gap_secondary_box.bind("<Return>", lambda e: self._on_gap_secondary_validate())

        self._en_gap = tk.BooleanVar(value=True)
        tk.Checkbutton(col_gap, text="Enabled", variable=self._en_gap,
                        bg=T["card_bg"], fg=T["text"], font=self._f_small,
                        activebackground=T["card_bg"]).pack(pady=(6, 0))

        # ═══════════════════════ Danger / Alarm 2 card ═══════════════════
        card2 = make_card(top_row, "Danger / Alarm 2", self._f_head)

        mode_row = tk.Frame(card2, bg=T["card_bg"])
        mode_row.pack(fill="x", pady=(0, 10))

        mode1 = ttk.Combobox(mode_row, values=["Direct", "Gap", "1X Amp", "2X Amp"],
                              font=self._f_small, state="readonly", width=8)
        mode1.set("Direct")
        mode1.pack(side="left")

        mode2 = ttk.Combobox(mode_row, values=["None", "Direct", "Gap"],
                              font=self._f_small, state="readonly", width=8)
        mode2.set("None")
        mode2.pack(side="left", padx=(8, 0))

        col_direct2 = tk.Frame(card2, bg=T["card_bg"])
        col_direct2.pack()

        tk.Label(col_direct2, text="Direct mil\npp", font=self._f_bold,
                  bg=T["card_bg"], fg=T["text"], justify="center").pack()

        self._entry_direct2 = self._value_box(col_direct2, self.direct2_value)
        self._entry_direct2.pack(pady=(2, 6))
        self._entry_direct2.bind("<KeyRelease>", lambda e: self._on_direct2_realtime())
        self._entry_direct2.bind("<FocusOut>", lambda e: self._on_direct2_validate())
        self._entry_direct2.bind("<Return>", lambda e: self._on_direct2_validate())

        c3 = tk.Canvas(col_direct2, width=70, height=250, bg=T["card_bg"], highlightthickness=0)
        c3.pack()
        self._canvas_direct2 = c3
        self._draw_gauge(
            c3, x=28, y=8, w=26, h=210,
            zones=[(0.00, 0.20, self.colors["gauge_red"]), (0.20, 1.00, self.colors["gauge_green"])],
            top_text=str(self.direct2_top), bottom_text=str(self.direct2_bottom),
            pointer_frac=self._frac(self.direct2_value, self.direct2_top, self.direct2_bottom),
        )

        self._en_direct2 = tk.BooleanVar(value=True)
        tk.Checkbutton(col_direct2, text="Enabled", variable=self._en_direct2,
                        bg=T["card_bg"], fg=T["text"], font=self._f_small,
                        activebackground=T["card_bg"]).pack(pady=(6, 0))

        # ═══════════════════════ Bottom bar ═══════════════════════
        tk.Frame(main, bg=T["group_border"], height=1).pack(fill="x", pady=(12, 10))

        bottom = tk.Frame(main, bg=T["win_bg"])
        bottom.pack(fill="x")

        chan_combo = ttk.Combobox(
            bottom, values=["channel 1", "channel 2", "channel 3", "channel 4"],
            font=self._f_small, state="readonly", width=10
        )
        chan_combo.set("channel 1")
        chan_combo.pack(side="left")

        monitor_combo = ttk.Combobox(
            bottom, values=["3000/12M/DIS", "3000/12M/DIS-A", "3000/12M/DIS-B"],
            font=self._f_small, state="readonly", width=14
        )
        monitor_combo.set(self.monitor_selection)
        monitor_combo.pack(side="left", padx=(12, 0))
        monitor_combo.bind("<<ComboboxSelected>>", self._on_monitor_change)

        vms_badge = tk.Label(
            bottom, text="VMS 3000", font=self._f_vms,
            bg=T["win_bg"], fg=T["vms_blue"]
        )
        vms_badge.pack(side="left", padx=(16, 0))

        make_pill_button(bottom, "Colors",   self._on_color_config,  self._f_norm, kind="outline")
        make_pill_button(bottom, "Cancel",   self._on_cancel,       self._f_norm, kind="outline")
        make_pill_button(bottom, "Defaults", self._on_set_defaults, self._f_norm, kind="outline", enabled=False)
        make_pill_button(bottom, "Copy",     self._on_copy,         self._f_norm, kind="outline")
        make_pill_button(bottom, "Ok",       self._on_ok,           self._f_norm, kind="primary")

    # ──────────────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────────────
    def _value_box(self, parent, value, small=False):
        entry = tk.Entry(
            parent, width=6 if not small else 6, justify="center",
            relief="sunken", bd=2, font=self._f_norm, bg=T["entry_bg"]
        )
        entry.insert(0, str(value))
        return entry

    @staticmethod
    def _frac(value, top, bottom):
        """Fraction of the gauge height from the TOP for a given value."""
        span = bottom - top
        if span == 0:
            return 0.0
        f = (value - top) / span
        return max(0.0, min(1.0, f))

    def _draw_gauge(self, canvas, x, y, w, h, zones, top_text, bottom_text,
                     pointer_frac=None, pointer2_frac=None, ticks=10):
        """Draw a vertical thermometer-style gauge with colour zones and pointer(s)."""
        canvas.create_rectangle(x, y, x + w, y + h, fill=T["gauge_track"],
                                 outline=T["gauge_border"], width=1)

        for f0, f1, color in zones:
            y0 = y + f0 * h
            y1 = y + f1 * h
            canvas.create_rectangle(x + 1, y0, x + w - 1, y1, fill=color, outline="")

        canvas.create_rectangle(x, y, x + w, y + h, outline=T["gauge_border"], width=1)

        for i in range(ticks + 1):
            ty = y + h * i / ticks
            canvas.create_line(x, ty, x + 7, ty, fill=self.colors["gauge_tick"])
            canvas.create_line(x + w - 7, ty, x + w, ty, fill=self.colors["gauge_tick"])

        canvas.create_text(x - 6, y, text=top_text, anchor="e", font=self._f_small, fill=T["text"])
        canvas.create_text(x - 6, y + h, text=bottom_text, anchor="e", font=self._f_small, fill=T["text"])

        if pointer_frac is not None:
            py = y + pointer_frac * h
            canvas.create_line(x - 5, py, x + w + 5, py, fill=self.colors["pointer"], width=2)

        if pointer2_frac is not None:
            py2 = y + pointer2_frac * h
            canvas.create_polygon(
                x + w + 5, py2, x + w + 13, py2 - 5, x + w + 13, py2 + 5,
                fill=self.colors["pointer2"], outline=""
            )

    # ──────────────────────────────────────────────────────────────────
    #  Button handlers
    # ──────────────────────────────────────────────────────────────────
    def _on_ok(self):
        print(f"Ok - setpoints applied for slot {self._slot_num}")
        self._dialog.destroy()

    def _on_copy(self):
        print(f"Copy setpoints for slot {self._slot_num}")

    def _on_cancel(self):
        self._dialog.destroy()

    def _on_set_defaults(self):
        print(f"Set defaults for slot {self._slot_num}")

    def _on_color_config(self):
        """Open color configuration dialog for setpoints gauges."""
        color_dlg = tk.Toplevel(self._dialog)

    def _on_monitor_change(self, event=None):
        """Handle monitor selection change."""
        combo = event.widget
        self.monitor_selection = combo.get()
        # Update gauges when monitor changes to 3000/12M/DIS
        if self.monitor_selection == "3000/12M/DIS":
            self._update_direct1_gauge()
            self._update_direct2_gauge()
            self._update_gap_gauge()
        else:
            # Reset to original multi-color zones when not 3000/12M/DIS
            self._reset_gauge_display()

    def _on_direct1_realtime(self):
        """Handle real-time Direct mil pp value changes for Alert/Alarm 1 (color updates while typing)."""
        try:
            value_str = self._entry_direct1.get()
            if value_str:  # Only process if there's some text
                value = float(value_str)
                # Update value for gauge display in real-time (without validation alert)
                self.direct1_value = value
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_direct1_gauge()
                else:
                    self._reset_gauge_display()
        except ValueError:
            # Invalid input during typing - ignore, let user finish typing
            pass

    def _on_direct1_validate(self):
        """Handle validation on FocusOut/Return for Alert/Alarm 1."""
        try:
            value = float(self._entry_direct1.get())
            # Validate value >= 10
            if value >= 10:
                self._show_alert_message("value cannot be '10' mil")
                # Reset to default valid value
                self.direct1_value = 3  # Reset to default
                self._entry_direct1.delete(0, tk.END)
                self._entry_direct1.insert(0, str(self.direct1_value))
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_direct1_gauge()
                else:
                    self._reset_gauge_display()
                return
            # Validate value must be less than Danger value
            if value >= self.direct2_value:
                self._show_alert_message("Alert value must be less than Danger value")
                # Reset to default valid value
                self.direct1_value = 3  # Reset to default
                self._entry_direct1.delete(0, tk.END)
                self._entry_direct1.insert(0, str(self.direct1_value))
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_direct1_gauge()
                else:
                    self._reset_gauge_display()
                return
            self.direct1_value = value
            if self.monitor_selection == "3000/12M/DIS":
                self._update_direct1_gauge()
            else:
                self._reset_gauge_display()
        except ValueError:
            # Invalid input, reset to default valid value
            self.direct1_value = 3  # Reset to default
            self._entry_direct1.delete(0, tk.END)
            self._entry_direct1.insert(0, str(self.direct1_value))
            if self.monitor_selection == "3000/12M/DIS":
                self._update_direct1_gauge()
            else:
                self._reset_gauge_display()

    def _on_direct2_realtime(self):
        """Handle real-time Direct mil pp value changes for Danger/Alarm 2 (color updates while typing)."""
        try:
            value_str = self._entry_direct2.get()
            if value_str:  # Only process if there's some text
                value = float(value_str)
                # Update value for gauge display in real-time (without validation alert)
                self.direct2_value = value
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_direct2_gauge()
                else:
                    self._reset_gauge_display()
        except ValueError:
            # Invalid input during typing - ignore, let user finish typing
            pass

    def _on_direct2_validate(self):
        """Handle validation on FocusOut/Return for Danger/Alarm 2."""
        try:
            value = float(self._entry_direct2.get())
            # Validate value >= 10
            if value >= 10:
                self._show_alert_message("value cannot be '10' mil")
                # Reset to default valid value
                self.direct2_value = 6  # Reset to default
                self._entry_direct2.delete(0, tk.END)
                self._entry_direct2.insert(0, str(self.direct2_value))
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_direct2_gauge()
                else:
                    self._reset_gauge_display()
                return
            # Validate value must be greater than Alert value
            if value <= self.direct1_value:
                self._show_alert_message("Danger value must be greater than Alert value")
                # Reset to default valid value
                self.direct2_value = 6  # Reset to default
                self._entry_direct2.delete(0, tk.END)
                self._entry_direct2.insert(0, str(self.direct2_value))
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_direct2_gauge()
                else:
                    self._reset_gauge_display()
                return
            self.direct2_value = value
            if self.monitor_selection == "3000/12M/DIS":
                self._update_direct2_gauge()
            else:
                self._reset_gauge_display()
        except ValueError:
            # Invalid input, reset to default valid value
            self.direct2_value = 6  # Reset to default
            self._entry_direct2.delete(0, tk.END)
            self._entry_direct2.insert(0, str(self.direct2_value))
            if self.monitor_selection == "3000/12M/DIS":
                self._update_direct2_gauge()
            else:
                self._reset_gauge_display()

    def _on_gap_realtime(self):
        """Handle real-time Gap Vdc value changes (color updates while typing)."""
        try:
            value_str = self._entry_gap.get()
            if value_str:  # Only process if there's some text
                value = float(value_str)
                # Update value for gauge display in real-time (without validation alert)
                self.gap_value = value
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_gap_gauge()
                else:
                    self._reset_gauge_display()
        except ValueError:
            # Invalid input during typing - ignore, let user finish typing
            pass

    def _on_gap_validate(self):
        """Handle validation on FocusOut/Return for Gap Vdc."""
        try:
            value = float(self._entry_gap.get())
            # Validate value outside normal range (-24 to 0)
            if value > 0 or value < -24:
                self._show_alert_message("value must be between -24 and 0 Vdc")
                # Reset to default valid value
                self.gap_value = -15.6  # Reset to default
                self._entry_gap.delete(0, tk.END)
                self._entry_gap.insert(0, str(self.gap_value))
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_gap_gauge()
                else:
                    self._reset_gauge_display()
                return
            self.gap_value = value
            if self.monitor_selection == "3000/12M/DIS":
                self._update_gap_gauge()
            else:
                self._reset_gauge_display()
        except ValueError:
            # Invalid input, reset to default valid value
            self.gap_value = -15.6  # Reset to default
            self._entry_gap.delete(0, tk.END)
            self._entry_gap.insert(0, str(self.gap_value))
            if self.monitor_selection == "3000/12M/DIS":
                self._update_gap_gauge()
            else:
                self._reset_gauge_display()

    def _on_gap_secondary_realtime(self):
        """Handle real-time Gap secondary value changes (color updates while typing)."""
        try:
            value_str = self._gap_secondary_box.get()
            if value_str:  # Only process if there's some text
                value = float(value_str)
                # Update value for gauge display in real-time (without validation alert)
                self.gap_secondary = value
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_gap_gauge()
                else:
                    self._reset_gauge_display()
        except ValueError:
            # Invalid input during typing - ignore, let user finish typing
            pass

    def _on_gap_secondary_validate(self):
        """Handle validation on FocusOut/Return for Gap secondary."""
        try:
            value = float(self._gap_secondary_box.get())
            # Validate value outside normal range (-24 to 0)
            if value > 0 or value < -24:
                self._show_alert_message("value must be between -24 and 0 Vdc")
                # Reset to default valid value
                self.gap_secondary = -8.4  # Reset to default
                self._gap_secondary_box.delete(0, tk.END)
                self._gap_secondary_box.insert(0, str(self.gap_secondary))
                if self.monitor_selection == "3000/12M/DIS":
                    self._update_gap_gauge()
                else:
                    self._reset_gauge_display()
                return
            self.gap_secondary = value
            if self.monitor_selection == "3000/12M/DIS":
                self._update_gap_gauge()
            else:
                self._reset_gauge_display()
        except ValueError:
            # Invalid input, reset to default valid value
            self.gap_secondary = -8.4  # Reset to default
            self._gap_secondary_box.delete(0, tk.END)
            self._gap_secondary_box.insert(0, str(self.gap_secondary))
            if self.monitor_selection == "3000/12M/DIS":
                self._update_gap_gauge()
            else:
                self._reset_gauge_display()

    def _show_alert_message(self, message="value cannot be '10' mil"):
        """Show alert message for invalid values."""
        alert = tk.Toplevel(self._dialog)
        alert.title("Alert")
        alert.geometry("300x120")
        alert.configure(bg=T["win_bg"])
        alert.resizable(False, False)
        alert.transient(self._dialog)
        alert.grab_set()

        tk.Label(
            alert, text=message,
            font=self._f_norm, bg=T["win_bg"], fg=T["text"],
            pady=20
        ).pack()

        tk.Button(
            alert, text="Ok", command=alert.destroy,
            font=self._f_norm, bg=T["btn_primary"], fg=T["btn_primary_fg"],
            relief="flat", bd=0, padx=50, pady=5,
            cursor="hand2"
        ).pack(pady=10)

        # Center the alert
        alert.update_idletasks()
        x = self._dialog.winfo_x() + (self._dialog.winfo_width() - alert.winfo_width()) // 2
        y = self._dialog.winfo_y() + (self._dialog.winfo_height() - alert.winfo_height()) // 2
        alert.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _update_direct1_gauge(self):
        """Update Direct mil pp gauge for Alert/Alarm 1 with color indication and movement."""
        if self._canvas_direct1:
            self._canvas_direct1.delete("all")
            # Determine color based on value
            if self.direct1_value <= 5:
                color = self.colors["gauge_green"]
            elif self.direct1_value <= 8:
                color = self.colors["gauge_yellow"]
            else:
                color = self.colors["gauge_red"]
            
            self._draw_gauge(
                self._canvas_direct1, x=28, y=8, w=26, h=210,
                zones=[(0.00, 1.00, color)],
                top_text=str(self.direct1_top), bottom_text=str(self.direct1_bottom),
                pointer_frac=self._frac(self.direct1_value, self.direct1_top, self.direct1_bottom),
            )

    def _update_direct2_gauge(self):
        """Update Direct mil pp gauge for Danger/Alarm 2 with color indication and movement."""
        if self._canvas_direct2:
            self._canvas_direct2.delete("all")
            # Determine color based on value
            if self.direct2_value <= 5:
                color = self.colors["gauge_green"]
            elif self.direct2_value <= 8:
                color = self.colors["gauge_yellow"]
            else:
                color = self.colors["gauge_red"]
            
            self._draw_gauge(
                self._canvas_direct2, x=28, y=8, w=26, h=210,
                zones=[(0.00, 1.00, color)],
                top_text=str(self.direct2_top), bottom_text=str(self.direct2_bottom),
                pointer_frac=self._frac(self.direct2_value, self.direct2_top, self.direct2_bottom),
            )

    def _update_gap_gauge(self):
        """Update Gap Vdc gauge with color indication and movement."""
        if self._canvas_gap:
            self._canvas_gap.delete("all")
            # Determine color based on value (Gap values are negative, so adjust logic)
            # Gap range is -24 to 0, so:
            # Green: values >= -15 (closer to 0)
            # Yellow: values between -20 and -15
            # Red: values <= -20 (farther from 0)
            if self.gap_value >= -15:
                color = self.colors["gauge_green"]
            elif self.gap_value >= -20:
                color = self.colors["gauge_yellow"]
            else:
                color = self.colors["gauge_red"]
            
            self._draw_gauge(
                self._canvas_gap, x=28, y=8, w=26, h=210,
                zones=[(0.00, 1.00, color)],
                top_text=str(self.gap_top), bottom_text=str(self.gap_bottom),
                pointer_frac=self._frac(self.gap_value, self.gap_top, self.gap_bottom),
                pointer2_frac=self._frac(self.gap_secondary, self.gap_top, self.gap_bottom),
            )

    def _reset_gauge_display(self):
        """Reset gauges to original multi-color zones when not 3000/12M/DIS."""
        # Reset Direct mil pp gauge 1
        if self._canvas_direct1:
            self._canvas_direct1.delete("all")
            self._draw_gauge(
                self._canvas_direct1, x=28, y=8, w=26, h=210,
                zones=[(0.00, 0.85, self.colors["gauge_yellow"]), (0.85, 1.00, self.colors["gauge_green"])],
                top_text=str(self.direct1_top), bottom_text=str(self.direct1_bottom),
                pointer_frac=self._frac(self.direct1_value, self.direct1_top, self.direct1_bottom),
            )
        
        # Reset Direct mil pp gauge 2
        if self._canvas_direct2:
            self._canvas_direct2.delete("all")
            self._draw_gauge(
                self._canvas_direct2, x=28, y=8, w=26, h=210,
                zones=[(0.00, 0.20, self.colors["gauge_red"]), (0.20, 1.00, self.colors["gauge_green"])],
                top_text=str(self.direct2_top), bottom_text=str(self.direct2_bottom),
                pointer_frac=self._frac(self.direct2_value, self.direct2_top, self.direct2_bottom),
            )
        
        # Reset Gap Vdc gauge
        if self._canvas_gap:
            self._canvas_gap.delete("all")
            self._draw_gauge(
                self._canvas_gap, x=28, y=8, w=26, h=210,
                zones=[(0.00, 0.12, self.colors["gauge_yellow"]),
                       (0.12, 0.62, self.colors["gauge_green"]),
                       (0.62, 1.00, self.colors["gauge_yellow"])],
                top_text=str(self.gap_top), bottom_text=str(self.gap_bottom),
                pointer_frac=self._frac(self.gap_value, self.gap_top, self.gap_bottom),
                pointer2_frac=self._frac(self.gap_secondary, self.gap_top, self.gap_bottom),
            )

    def _on_color_config(self):
        """Open color configuration dialog for setpoints gauges."""
        color_dlg = tk.Toplevel(self._dialog)
        color_dlg.title("Color Configuration")
        color_dlg.geometry("450x400")
        color_dlg.configure(bg=T["win_bg"])
        color_dlg.resizable(False, False)
        color_dlg.transient(self._dialog)
        color_dlg.grab_set()

        # Title bar matching menu bar standard
        titlebar = tk.Frame(color_dlg, bg=T["titlebar"], height=32)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)

        tk.Label(titlebar, text="  Color Configuration", font=self._f_bold,
                bg=T["titlebar"], fg=T["card_header_fg"], anchor="w").pack(side="left", fill="x", expand=True)

        # Main content area with card styling
        main = tk.Frame(color_dlg, bg=T["win_bg"], padx=12, pady=12)
        main.pack(fill="both", expand=True)

        # Card for color settings
        card_outer = tk.Frame(main, bg=T["group_border"])
        card_outer.pack(fill="both", expand=True)

        card = tk.Frame(card_outer, bg=T["card_bg"])
        card.pack(fill="both", expand=True, padx=1, pady=1)

        # Card header
        header = tk.Frame(card, bg=T["card_header"])
        header.pack(fill="x")

        spaced_title = " ".join(list("GAUGE COLORS".upper()))
        tk.Label(header, text=spaced_title, font=self._f_head,
                bg=T["card_header"], fg=T["card_header_fg"],
                anchor="w", padx=12, pady=6).pack(fill="x")

        # Card body
        card_body = tk.Frame(card, bg=T["card_bg"], padx=12, pady=10)
        card_body.pack(fill="both", expand=True)

        # Color configuration fields
        color_vars = {}
        color_labels = {
            "gauge_yellow": "Gauge Yellow",
            "gauge_green": "Gauge Green",
            "gauge_red": "Gauge Red",
            "gauge_tick": "Gauge Tick",
            "pointer": "Pointer",
            "pointer2": "Secondary Pointer",
        }

        for key, label in color_labels.items():
            row = tk.Frame(card_body, bg=T["card_bg"])
            row.pack(fill="x", pady=3)

            tk.Label(row, text=label, font=self._f_norm, bg=T["card_bg"], fg=T["text"],
                      width=18, anchor="w").pack(side="left")

            var = tk.StringVar(value=self.colors[key])
            color_vars[key] = var

            entry = tk.Entry(row, textvariable=var, width=10, font=self._f_norm,
                           bg="#ffffff", relief="sunken", bd=2,
                           highlightthickness=1, highlightbackground=T["btn_border"])
            entry.pack(side="left", padx=(8, 5))

            # Color preview box
            preview = tk.Frame(row, width=35, height=22, bg=self.colors[key],
                              relief="solid", bd=1)
            preview.pack(side="left")

            # Update preview when entry changes
            def update_preview(key=key, preview=preview, var=var):
                def on_change(*args):
                    preview.configure(bg=var.get())
                var.trace_add("write", on_change)
            update_preview()

        # Button frame with toolbar-style buttons
        btn_frame = tk.Frame(main, bg=T["win_bg"])
        btn_frame.pack(fill="x", pady=(12, 0))

        def apply_colors():
            for key, var in color_vars.items():
                self.colors[key] = var.get()
            # Refresh gauges
            self._build_ui()
            color_dlg.destroy()

        def reset_colors():
            self.colors = {
                "gauge_yellow": T["gauge_yellow"],
                "gauge_green": T["gauge_green"],
                "gauge_red": T["gauge_red"],
                "gauge_tick": T["gauge_tick"],
                "pointer": T["pointer"],
                "pointer2": T["pointer2"],
            }
            color_dlg.destroy()
            self._build_ui()

        # Toolbar-style buttons
        make_pill_button(btn_frame, "Apply", apply_colors, self._f_norm, kind="primary")
        make_pill_button(btn_frame, "Reset", reset_colors, self._f_norm, kind="outline")
        make_pill_button(btn_frame, "Cancel", color_dlg.destroy, self._f_norm, kind="outline")


# ══════════════════════════════════════════════════════════════════════════
#  Standalone demo
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    root.title("VMS 3000 Demo Host")
    root.geometry("300x120")

    def open_dialog():
        dlg = SetpointsDialog(root, {}, slot_num=4)
        dlg.show()

    tk.Button(root, text="Open Setpoints - Radial Vibration...",
              command=open_dialog, wraplength=260).pack(expand=True, padx=20, pady=20)

    root.mainloop()