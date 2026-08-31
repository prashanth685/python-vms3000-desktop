"""
relay_config.py — VMS 3000 Relay Configuration Dialog
Classic-style relay configuration dialog, matching the legacy VMS 3000
"Relay Configuration" screen exactly:
  - Rack Type / Config ID / Relay Slot header
  - Available Slots rack graphic (10 module slots, selected slot highlighted)
  - Available Monitor channels / Alarms list
  - Logic keypad: And(*), Or(+), (, ), Enter, <-, CLR, Copy  + percent readout
  - Standard Relay Association: channel dropdown, Active / Latching Relay,
    And Voting Setup
  - Alarm Drive Logic text box
  - Relay NE/NDE Switch Status line
  - Bottom bar: Ok, Point Names, Cancel, Print, Help, VMS 3000 badge
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import sys
import os
from PIL import Image, ImageTk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# ── Classic "Windows Classic" gray theme, matching the reference screenshot ──
# Falls back to this if the project theme.py isn't available / doesn't define
# these classic-look keys (the modern teal/card theme doesn't apply to this
# legacy-style dialog).
try:
    from theme import T as _PROJECT_T
except Exception:
    _PROJECT_T = {}

CLASSIC = {
    "win_bg":       "#dbe4f0",   # light blue-gray dialog face (matches reference photo)
    "group_bg":     "#dbe4f0",
    "field_bg":     "#ffffff",
    "text":         "#000000",
    "text_dim":     "#000000",
    "border_dark":  "#7f8a9a",
    "border_light": "#ffffff",
    "border_black": "#000000",
    "btn_face":     "#dbe4f0",
    "btn_hover":    "#eaf0f8",
    "accent":       "#0d3fa0",   # VMS 3000 badge blue
    "slot_dark":    "#0a2a52",
    "slot_mid":     "#1c4d82",
    "slot_light":   "#3f7ab5",
    "slot_selected":"#79b8e8",
    "led_green":    "#3fdc5a",
    "led_yellow":   "#e8d23f",
    "lcd_bg":       "#0b0f14",
}
T = {**CLASSIC, **{k: v for k, v in _PROJECT_T.items() if k not in CLASSIC}}

FONT_NAME = "MS Sans Serif"


# ══════════════════════════════════════════════════════════════════════════
#  Classic bevel helpers
# ══════════════════════════════════════════════════════════════════════════

def sunken_frame(parent, **kw):
    """A frame with a classic sunken (etched-in) border."""
    f = tk.Frame(parent, bg=T["win_bg"], bd=2, relief="sunken", **kw)
    return f


def group_box(parent, title, font):
    """Classic Windows GroupBox: an etched (sunken) double-line border with a
    title label cut into the top-left of the border. Returns the inner
    content frame."""
    outer = tk.Frame(parent, bg=T["win_bg"])

    # Reserve space ABOVE the border for the title label. Previously the
    # label was placed at y=0, anchor="w" (vertically centered on the
    # border line) which put half its height above the outer frame's own
    # top edge — outside the parent's drawable area — so headings like
    # "Available Slots" / "Standard Relay Association" were clipped and
    # barely legible. Now the border starts a few pixels lower and the
    # label is anchored "nw" at y=0, so the full heading is always shown.
    label_clear = max(14, font.metrics("linespace"))
    dark = tk.Frame(outer, bg=T["border_dark"])
    dark.pack(fill="both", expand=True, pady=(label_clear // 2, 0))
    light = tk.Frame(dark, bg=T["border_light"])
    light.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
    inner = tk.Frame(light, bg=T["win_bg"])
    inner.pack(fill="both", expand=True, padx=1, pady=1)

    content = tk.Frame(inner, bg=T["win_bg"])
    content.pack(fill="both", expand=True, padx=8, pady=(10, 8))

    # Title label sits on top of the border, with a background patch behind
    # it so the border line doesn't show through the text.
    lbl = tk.Label(outer, text=title, font=font, bg=T["win_bg"], fg=T["text"], padx=4)
    lbl.place(x=8, y=0, anchor="nw")

    return outer, content


def classic_button(parent, text, command, font, width=None, enabled=True):
    """A raised classic beveled button."""
    b = tk.Button(
        parent, text=text, command=command, font=font,
        bg=T["btn_face"], fg=T["text"], activebackground=T["btn_hover"],
        relief="raised", bd=2, padx=6, pady=2,
        highlightthickness=0, width=width,
        state="normal" if enabled else "disabled",
    )
    return b


# ══════════════════════════════════════════════════════════════════════════
#  Relay Configuration Dialog
# ══════════════════════════════════════════════════════════════════════════

class RelayConfigDialog:
    """Relay Configuration dialog — classic VMS 3000 layout."""

    NUM_SLOTS = 11

    def __init__(self, parent, slot_num, rack_type, config_id, selected_slot=4, rack_config=None):
        self._parent = parent
        self._slot_num = slot_num
        self._rack_type = rack_type
        self._config_id = config_id
        self._selected_slot = selected_slot
        self._rack_config = rack_config or {}  # Saved rack configuration data
        self._dialog = None

        # ── Full data model — every field visible in the reference dialog ──
        self.config_data = {
            "rack_type": rack_type,
            "config_id": config_id,
            "relay_slot": slot_num,
            "selected_slot": selected_slot,
            "monitor_channels": [],          # "Available Monitor channels/ Alarms" list
            "logic_expression": "",          # built via And/Or/(/)/Enter keypad
            "logic_percent": 0,              # "0%" readout under keypad
            "channel_association": "Channel 1",
            "active": False,
            "latching_relay": False,
            "alarm_drive_logic": "",
            "ne_nde_switch_status": "",
        }

    # ──────────────────────────────────────────────────────────────────
    def show(self):
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title("Relay Configuration")
        self._dialog.geometry("700x560")
        self._dialog.minsize(680, 520)
        self._dialog.configure(bg=T["win_bg"])
        self._dialog.resizable(True, True)

        self._dialog.transient(self._parent)
        self._dialog.grab_set()

        self._f_norm  = tkfont.Font(family=FONT_NAME, size=8)
        self._f_bold  = tkfont.Font(family=FONT_NAME, size=8, weight="bold")
        self._f_small = tkfont.Font(family=FONT_NAME, size=7)
        self._f_group = tkfont.Font(family=FONT_NAME, size=8, weight="bold")
        self._f_vms   = tkfont.Font(family=FONT_NAME, size=13, weight="bold", slant="italic")

        self._build_ui()

        self._dialog.update_idletasks()
        x = self._parent.winfo_x() + (self._parent.winfo_width() - self._dialog.winfo_width()) // 2
        y = self._parent.winfo_y() + (self._parent.winfo_height() - self._dialog.winfo_height()) // 2
        self._dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        main = tk.Frame(self._dialog, bg=T["win_bg"], padx=8, pady=8)
        main.pack(fill="both", expand=True)

        # ═══════════════════ Header: Rack Type / Config ID / Relay Slot ════
        header = tk.Frame(main, bg=T["win_bg"])
        header.pack(fill="x", pady=(0, 8))

        tk.Label(header, text="Rack Type:", font=self._f_bold,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left")
        tk.Label(header, text=self._rack_type, font=self._f_norm,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left", padx=(4, 24))

        tk.Label(header, text="Config ID:", font=self._f_bold,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left")
        tk.Label(header, text=self._config_id or "", font=self._f_norm,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left", padx=(4, 24))

        tk.Label(header, text="Relay Slot:", font=self._f_bold,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left")
        tk.Label(header, text=str(self._slot_num), font=self._f_norm,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left", padx=(4, 0))

        # ═══════════════════ Top split: Slots | Monitor channels ═══════════
        # In the reference dialog, "Available Slots" is the wider left box
        # (rack graphic + logic keypad side-by-side, INSIDE the same box),
        # and "Available Monitor channels/ Alarms" is the narrower right box.
        top_split = tk.Frame(main, bg=T["win_bg"])
        top_split.pack(fill="both", expand=True)
        top_split.grid_columnconfigure(0, weight=58, minsize=380)
        top_split.grid_columnconfigure(1, weight=42, minsize=240)
        top_split.grid_rowconfigure(0, weight=1, minsize=190)

        # ---- Left: Available Slots (rack graphic + keypad together) ----
        slots_outer, slots_body = group_box(top_split, "Available Slots", self._f_group)
        slots_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        slots_split = tk.Frame(slots_body, bg=T["win_bg"])
        slots_split.pack(fill="both", expand=True)

        rack_col = tk.Frame(slots_split, bg=T["win_bg"])
        rack_col.pack(side="left", fill="both", expand=True)
        self._build_slots_rack(rack_col)

        keypad_col = tk.Frame(slots_split, bg=T["win_bg"])
        keypad_col.pack(side="left", padx=(8, 0))
        self._build_keypad(keypad_col)

        # ---- Right: Available Monitor channels/ Alarms ----
        mon_outer, mon_body = group_box(top_split, "Available Monitor channels/ Alarms", self._f_group)
        mon_outer.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self._build_monitor_list(mon_body)

        # Now that both the rack graphic and the monitor list exist, show the
        # Available Monitor channels/Alarms for whichever slot starts selected
        # (e.g. the 3000/12M/DIS slot), matching the reference behaviour.
        self._on_slot_selected(self.config_data["selected_slot"])

        # ═══════════════════ Bottom split: Association | Alarm Logic ═══════
        bottom_split = tk.Frame(main, bg=T["win_bg"])
        bottom_split.pack(fill="both", expand=True, pady=(8, 0))

        assoc_outer, assoc_body = group_box(bottom_split, "Standard Relay Association", self._f_group)
        assoc_outer.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self._build_relay_association(assoc_body)

        logic_outer, logic_body = group_box(bottom_split, "Alarm Drive Logic", self._f_group)
        logic_outer.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self._build_alarm_drive_logic(logic_body)

        # ═══════════════════ NE/NDE Switch Status ═══════════════════════
        status_row = tk.Frame(main, bg=T["win_bg"])
        status_row.pack(fill="x", pady=(8, 6))

        tk.Label(status_row, text="Relay NE/NDE Switch Status:", font=self._f_bold,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left")
        self._status_value = tk.Label(status_row, textvariable=None, text="",
                                       font=self._f_norm, bg=T["win_bg"], fg=T["text"])
        self._status_value.pack(side="left", padx=(6, 0))

        # ═══════════════════ Bottom button bar ═══════════════════════
        self._build_bottom_bar(main)

    # ──────────────────────────────────────────────────────────────────
    #  Available Slots rack graphic
    # ──────────────────────────────────────────────────────────────────
    def _build_slots_rack(self, parent):
        canvas_h = 168
        canvas = tk.Canvas(parent, height=canvas_h, bg=T["field_bg"],
                            highlightthickness=1, highlightbackground=T["border_dark"])
        canvas.pack(fill="x")
        self._slots_canvas = canvas
        self._slot_photos = {}  # keep PhotoImage refs alive (avoid GC)

        n = self.NUM_SLOTS
        pad = 4
        num_y = 12          # slot-number row, fully inside the canvas top edge
        top_y = 26           # module image top
        bot_y = canvas_h - 22  # module image bottom (room left for name row below)
        name_y = canvas_h - 10  # module short-name row, under the image

        self._rack_n = n
        self._rack_pad = pad

        def redraw(event=None):
            canvas.delete("all")
            width = canvas.winfo_width()
            if width < 10:
                width = 480
            slot_w = (width - 2 * pad) / n
            selected = self.config_data["selected_slot"]

            # Every slot is drawn at the SAME size — no enlarge/zoom for the
            # selected slot. Selection is shown only via a highlight border.
            for i in range(1, n + 1):
                x0 = pad + (i - 1) * slot_w
                x1 = x0 + slot_w - 2
                cx = (x0 + x1) / 2
                is_selected = (i == selected)

                # ── real module image, scaled to FIT the slot (aspect kept,
                #    not stretched/zoomed) — reflects whatever is actually
                #    assigned to this slot in the live rack configuration. ──
                module = self._rack_config.get(f"0_{i}")
                filename = self._resolve_module_image(module)
                box_w = max(1, (x1 - x0) - 4)
                box_h = max(1, (bot_y - top_y) - 4)
                photo = self._load_fit_photo(filename, box_w, box_h)

                if photo is not None:
                    cy = (top_y + bot_y) / 2
                    canvas.create_image(cx, cy, image=photo, anchor="center")
                    self._slot_photos[i] = photo

                if is_selected:
                    canvas.create_rectangle(x0, top_y, x1, bot_y, outline="#ffffff", width=2)
                    canvas.create_rectangle(x0 - 1, top_y - 1, x1 + 1, bot_y + 1,
                                             outline=T["accent"], width=1)

                # ── Slot number: drawn LAST (on top of the module image) with
                #    a high-contrast chip behind it, so it is always readable
                #    instead of being covered/washed out by the module photo. ──
                num_text = str(i)
                chip_w = max(14, self._f_bold.measure(num_text) + 8)
                chip_h = self._f_bold.metrics("linespace") + 2
                canvas.create_rectangle(
                    cx - chip_w / 2, num_y - chip_h / 2,
                    cx + chip_w / 2, num_y + chip_h / 2,
                    fill="#fdf6c9", outline=T["border_dark"],
                )
                canvas.create_text(cx, num_y, text=num_text,
                                    font=self._f_bold, fill="#000000")

                # ── Module short-name, shown under the image so the actual
                #    installed module type is always identified at a glance
                #    (e.g. "DIS", "6M", "RLY", "—") — matches the reference
                #    rack's slot labelling. ──
                short_name = self._short_module_label(module)
                canvas.create_text(cx, name_y, text=short_name,
                                    font=self._f_small, fill=T["text_dim"])

        canvas.bind("<Configure>", redraw)
        canvas.bind("<Button-1>", self._on_rack_click)
        canvas.configure(cursor="hand2")
        self._redraw_slots_rack = redraw
        self._dialog.after(50, redraw)

    def _on_rack_click(self, event):
        """Clicking a slot in the Available Slots graphic selects it —
        highlights it and refreshes the Available Monitor channels/Alarms
        list for whatever module is installed there (e.g. 3000/12M/DIS)."""
        canvas = self._slots_canvas
        width = canvas.winfo_width()
        if width < 10:
            return
        n = self._rack_n
        pad = self._rack_pad
        slot_w = (width - 2 * pad) / n
        i = int((event.x - pad) // slot_w) + 1
        i = max(1, min(n, i))
        self._on_slot_selected(i)

    def _on_slot_selected(self, slot_num):
        """Select a slot in the rack graphic and populate the Available
        Monitor channels/Alarms list for the module installed there."""
        self.config_data["selected_slot"] = slot_num

        if hasattr(self, "_redraw_slots_rack"):
            self._redraw_slots_rack()

        module = self._rack_config.get(f"0_{slot_num}")
        entries = self._monitor_entries_for_slot(slot_num, module)
        self.config_data["monitor_channels"] = entries

        if hasattr(self, "_monitor_listbox"):
            self._monitor_listbox.delete(0, "end")
            for entry in entries:
                self._monitor_listbox.insert("end", entry)

    @staticmethod
    def _channel_count_for_module(module):
        """Number of monitored channels for a given module type — drives how
        many Alert/Danger rows appear in Available Monitor channels/Alarms."""
        if not module or module == "No Modules":
            return 0
        if module == "3000/12M/DIS":
            return 4
        if module in ("VMM-6M", "3000/6M"):
            return 2
        upper = module.upper()
        if "TAC" in upper:
            return 2
        return 0

    def _monitor_entries_for_slot(self, slot_num, module):
        """Build the Available Monitor channels/Alarms entries for a slot,
        matching the reference naming exactly:
          S{slot}C##A1 (Slot {slot} Any Active Alert)
          S{slot}C##A2 (Slot {slot} Any Active Danger)
          S{slot}C{ch:02d}A1 (Slot {slot} Channel {ch} Alert)
          S{slot}C{ch:02d}A2 (Slot {slot} Channel {ch} Danger)
        Returns an empty list for slots with no monitored channels (empty
        slots, Relay modules, etc.)."""
        n_channels = self._channel_count_for_module(module)
        if n_channels <= 0:
            return []

        entries = [
            f"S{slot_num}C##A1 (Slot {slot_num} Any Active Alert)",
            f"S{slot_num}C##A2 (Slot {slot_num} Any Active Danger)",
        ]
        for ch in range(1, n_channels + 1):
            entries.append(f"S{slot_num}C{ch:02d}A1 (Slot {slot_num} Channel {ch} Alert)")
            entries.append(f"S{slot_num}C{ch:02d}A2 (Slot {slot_num} Channel {ch} Danger)")
        return entries

    @staticmethod
    def _short_module_label(module):
        """Short, always-legible label shown under each slot's image in the
        Available Slots rack graphic — identifies the installed module type
        at a glance (e.g. 'DIS', '6M', 'RLY', '—' for empty)."""
        if not module or module == "No Modules":
            return "\u2014"
        if module == "3000/12M/DIS":
            return "DIS"
        if module in ("VMM-6M", "3000/6M"):
            return "6M"
        upper = module.upper()
        if "RLY" in upper or "RELAY" in upper:
            return "RLY"
        if "TAC" in upper:
            return "TAC"
        return module[:6]

    @staticmethod
    def _resolve_module_image(module):
        """Map an assigned module name to its real rack image filename
        (same images used in the main rack view)."""
        if not module or module == "No Modules":
            return "NO_Module.jpg"
        if module == "3000/12M/DIS":
            return "Measurement_Module.jpg"
        if module in ("VMM-6M", "3000/6M"):
            return "VMM-6M.jpg"
        upper = module.upper()
        if "RLY" in upper or "RELAY" in upper:
            return "Relay_Module.jpg"
        return "NO_Module.jpg"

    def _load_fit_photo(self, filename, box_w, box_h):
        """Load src/images/<filename> and scale it to FIT inside
        (box_w x box_h) preserving aspect ratio — contain, not stretch/zoom."""
        box_w = max(1, int(round(box_w)))
        box_h = max(1, int(round(box_h)))

        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, "..", "images", filename)
        if not os.path.exists(img_path):
            return None

        try:
            img = Image.open(img_path).convert("RGB")
            src_w, src_h = img.size
            scale = min(box_w / src_w, box_h / src_h)
            new_w = max(1, int(round(src_w * scale)))
            new_h = max(1, int(round(src_h * scale)))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    # ──────────────────────────────────────────────────────────────────
    #  Logic keypad: And(*) Or(+) ( ) Enter <- CLR Copy  + % readout
    # ──────────────────────────────────────────────────────────────────
    def _build_keypad(self, parent):
        grid = tk.Frame(parent, bg=T["win_bg"])
        grid.pack(side="left")

        def add(txt):
            # Insert directly into the Alarm Drive Logic box at the cursor,
            # so the keypad's And/Or/(/) presses are visibly reflected there
            # (matching the reference behaviour) rather than only being
            # tracked in an invisible internal string.
            self._insert_logic_text(txt)

        btn_font = self._f_norm
        r1 = tk.Frame(grid, bg=T["win_bg"]); r1.pack()
        classic_button(r1, "And [*]", lambda: add("*"), btn_font, width=7).pack(side="left", padx=2, pady=2)
        classic_button(r1, "Or [+]", lambda: add("+"), btn_font, width=7).pack(side="left", padx=2, pady=2)
        r2 = tk.Frame(grid, bg=T["win_bg"]); r2.pack()
        classic_button(r2, "(", lambda: add("("), btn_font, width=7).pack(side="left", padx=2, pady=2)
        classic_button(r2, ")", lambda: add(")"), btn_font, width=7).pack(side="left", padx=2, pady=2)

        enter_holder = tk.Frame(parent, bg=T["win_bg"])
        enter_holder.pack(side="left", padx=6)
        classic_button(enter_holder, "Enter", self._on_logic_enter, self._f_bold,
                        width=6).pack(fill="both", expand=True, ipady=14)

        side_col = tk.Frame(parent, bg=T["win_bg"])
        side_col.pack(side="left", padx=(8, 0))
        classic_button(side_col, "<-", self._on_logic_backspace, btn_font, width=6).pack(pady=2, fill="x")
        classic_button(side_col, "CLR", self._on_logic_clear, btn_font, width=6).pack(pady=2, fill="x")
        classic_button(side_col, "Copy", self._on_copy, btn_font, width=6).pack(pady=2, fill="x")

        pct_row = tk.Frame(parent, bg=T["win_bg"])
        pct_row.pack(side="bottom", fill="x", pady=(6, 0))

        track = tk.Frame(pct_row, bg=T["field_bg"], bd=2, relief="sunken", height=8)
        track.pack(side="left", fill="x", expand=True, padx=(0, 6))
        track.pack_propagate(False)

        self._pct_var = tk.StringVar(value=f'{self.config_data["logic_percent"]}%')
        tk.Label(pct_row, textvariable=self._pct_var, font=self._f_small,
                 bg=T["win_bg"], fg=T["text"]).pack(side="left")

    # ── Alarm Drive Logic text helpers — the logic box is the single
    #    visible source of truth; the keypad, the monitor-channel list,
    #    and Enter/backspace/CLR all read from and write to it directly. ──
    def _insert_logic_text(self, text):
        """Insert text into the Alarm Drive Logic box at the cursor (or at
        the end if the box doesn't have focus yet), then sync config_data."""
        widget = getattr(self, "_alarm_logic_text", None)
        if widget is None:
            self.config_data["logic_expression"] += text
            return
        try:
            widget.insert("insert", text)
        except tk.TclError:
            widget.insert("end", text)
        widget.see("insert")
        widget.focus_set()
        self.config_data["logic_expression"] = widget.get("1.0", "end-1c")

    def _on_logic_enter(self):
        widget = getattr(self, "_alarm_logic_text", None)
        if widget is not None:
            self.config_data["logic_expression"] = widget.get("1.0", "end-1c")
        print(f"Enter logic expression: {self.config_data['logic_expression']}")

    def _on_logic_backspace(self):
        widget = getattr(self, "_alarm_logic_text", None)
        if widget is not None:
            widget.delete("insert-1c", "insert")
            widget.focus_set()
            self.config_data["logic_expression"] = widget.get("1.0", "end-1c")
        else:
            self.config_data["logic_expression"] = self.config_data["logic_expression"][:-1]

    def _on_logic_clear(self):
        widget = getattr(self, "_alarm_logic_text", None)
        if widget is not None:
            widget.delete("1.0", "end")
            widget.focus_set()
        self.config_data["logic_expression"] = ""
        self.config_data["logic_percent"] = 0
        self._pct_var.set("0%")

    # ──────────────────────────────────────────────────────────────────
    #  Available Monitor channels/ Alarms
    # ──────────────────────────────────────────────────────────────────
    def _build_monitor_list(self, parent):
        list_frame = sunken_frame(parent)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self._monitor_listbox = tk.Listbox(
            list_frame, font=self._f_norm, bg=T["field_bg"], fg=T["text"],
            relief="flat", bd=0, selectmode="browse",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self._monitor_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self._monitor_listbox.pack(side="left", fill="both", expand=True)

        self._monitor_listbox.bind("<<ListboxSelect>>", self._on_monitor_channel_select)

        for ch in self.config_data["monitor_channels"]:
            self._monitor_listbox.insert("end", ch)

    def _on_monitor_channel_select(self, event=None):
        """Selecting a channel/alarm entry (e.g. 'S5C01A1 (Slot 5 Channel 1
        Alert)') inserts just its point code into the Alarm Drive Logic box
        at the cursor, so building a logic expression from monitor points
        works the same way as using the And/Or/(/) keypad."""
        sel = self._monitor_listbox.curselection()
        if not sel:
            return
        entry = self._monitor_listbox.get(sel[0])
        code = entry.split(" ", 1)[0]
        self._insert_logic_text(code)

    # ──────────────────────────────────────────────────────────────────
    #  Standard Relay Association
    # ──────────────────────────────────────────────────────────────────
    def _build_relay_association(self, parent):
        tk.Label(parent, text="Channel Association", font=self._f_norm,
                 bg=T["win_bg"], fg=T["text"]).pack(anchor="w")

        self._channel_combo = ttk.Combobox(
            parent, values=[f"Channel {i}" for i in range(1, 9)],
            font=self._f_norm, state="readonly", width=18,
        )
        self._channel_combo.set(self.config_data["channel_association"])
        self._channel_combo.pack(anchor="w", pady=(2, 8), fill="x")

        self._active_var = tk.BooleanVar(value=self.config_data["active"])
        tk.Checkbutton(parent, text="Active", variable=self._active_var,
                        font=self._f_norm, bg=T["win_bg"], fg=T["text"],
                        activebackground=T["win_bg"]).pack(anchor="w")

        self._latching_var = tk.BooleanVar(value=self.config_data["latching_relay"])
        tk.Checkbutton(parent, text="Latching Relay", variable=self._latching_var,
                        font=self._f_norm, bg=T["win_bg"], fg=T["text"],
                        activebackground=T["win_bg"]).pack(anchor="w")

        classic_button(parent, "And Voting Setup", self._on_voting_setup,
                        self._f_norm).pack(anchor="w", pady=(10, 0), fill="x")

    def _on_voting_setup(self):
        print(f"And Voting Setup for slot {self._slot_num}")

    # ──────────────────────────────────────────────────────────────────
    #  Alarm Drive Logic
    # ──────────────────────────────────────────────────────────────────
    def _build_alarm_drive_logic(self, parent):
        text_frame = sunken_frame(parent)
        text_frame.pack(fill="both", expand=True)

        self._alarm_logic_text = tk.Text(
            text_frame, font=self._f_norm, bg=T["field_bg"], fg=T["text"],
            relief="flat", bd=0, wrap="word", height=6,
        )
        self._alarm_logic_text.insert("1.0", self.config_data["alarm_drive_logic"])
        self._alarm_logic_text.pack(fill="both", expand=True)

    # ──────────────────────────────────────────────────────────────────
    #  Bottom button bar
    # ──────────────────────────────────────────────────────────────────
    def _build_bottom_bar(self, main):
        tk.Frame(main, bg=T["border_dark"], height=1).pack(fill="x", pady=(0, 6))

        bottom = tk.Frame(main, bg=T["win_bg"])
        bottom.pack(fill="x")

        classic_button(bottom, "Ok", self._on_ok, self._f_norm, width=10).pack(side="left", padx=2)
        classic_button(bottom, "Point Names", self._on_point_names, self._f_norm, width=10).pack(side="left", padx=2)
        classic_button(bottom, "Cancel", self._on_cancel, self._f_norm, width=10).pack(side="left", padx=2)
        classic_button(bottom, "Print", self._on_print, self._f_norm, width=10).pack(side="left", padx=2)
        classic_button(bottom, "Help", self._on_help, self._f_norm, width=10).pack(side="left", padx=2)

        tk.Label(bottom, text="VMS 3000", font=self._f_vms,
                 bg=T["win_bg"], fg=T["accent"]).pack(side="right", padx=(4, 0))

    # ──────────────────────────────────────────────────────────────────
    #  Button handlers
    # ──────────────────────────────────────────────────────────────────
    def _on_ok(self):
        self.config_data["channel_association"] = self._channel_combo.get()
        self.config_data["active"] = self._active_var.get()
        self.config_data["latching_relay"] = self._latching_var.get()
        self.config_data["alarm_drive_logic"] = self._alarm_logic_text.get("1.0", "end-1c")
        self.config_data["monitor_channels"] = list(self._monitor_listbox.get(0, "end"))
        print(f"Ok — relay configuration applied for slot {self._slot_num}: {self.config_data}")
        self._dialog.destroy()

    def _on_point_names(self):
        print(f"Point Names for slot {self._slot_num}")

    def _on_cancel(self):
        self._dialog.destroy()

    def _on_print(self):
        print(f"Print relay configuration for slot {self._slot_num}")

    def _on_help(self):
        print("Help — Relay Configuration")

    def _on_copy(self):
        print(f"Copy relay configuration for slot {self._slot_num}")


# ══════════════════════════════════════════════════════════════════════════
#  Standalone demo
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    root.title("VMS 3000 Demo Host")
    root.geometry("300x120")

    def open_dialog():
        dlg = RelayConfigDialog(root, slot_num=1, rack_type="Standard Relay", config_id="", selected_slot=4)
        dlg.show()

    tk.Button(root, text="Open Relay Configuration...",
              command=open_dialog, wraplength=260).pack(expand=True, padx=20, pady=20)

    root.mainloop()