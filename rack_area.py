import tkinter as tk
import tkinter.font as tkfont
from theme import T
import sys
import os
import math
import traceback
from PIL import Image, ImageTk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from popups.configuration_settings import ConfigurationSettingsPopup
from popups.monitors import CascadingMenu
from popups.module_switch_confirmation import ModuleSwitchConfirmationPopup
from snapshot.racksnapshot import get_module_config, is_image_display_module
from points.point_options import PointOptionsContextMenu
from points.setpoins import SetpointsDialog
from points.proximiter12m_ridial import ProximityMonitor3000ConfigDialog
from points.relay_config import RelayConfigDialog
from points.sixm_option import SixMOptionsDialog

SLOT_COUNT = 12

# Modules that consume 2 slots and show the Measurement Module image
DIS_MODULE = "3000/12M/DIS"
VMM_MODULE = "VMM-6M"   # single-slot image (existing behaviour)
RLY_MODULE = "3000/RLY"  # single-slot Relay module image (fallback exact name)
SIXM_MODULE = "3000/6M"  # 3000/6M module


def _is_6m_module(module: str) -> bool:
    """
    Check if module is a 3000/6M module.
    """
    if not module:
        return False
    if module == SIXM_MODULE:
        return True
    upper = module.upper()
    return "6M" in upper and "3000" in upper


def _is_relay_module(module: str) -> bool:
    """
    Flexible Relay-module check. Matches the exact RLY_MODULE string OR
    any module name containing 'RLY' / 'RELAY' (case-insensitive), so this
    keeps working even if the exact label in the module-selection list
    differs slightly from RLY_MODULE (e.g. 'Relay', '3000/12M/RLY', etc.).
    """
    if not module:
        return False
    if module == RLY_MODULE:
        return True
    upper = module.upper()
    return "RLY" in upper or "RELAY" in upper


def _find_image_case_insensitive(base_dir, filename, subfolders):
    """
    Search a list of subfolders (relative to base_dir) for `filename`,
    ignoring case. Returns the first match found on disk, or None.

    subfolders: list of tuples, e.g. [('src', 'images'), ('images',), ()]
    An empty tuple () means "look directly in base_dir".
    """
    target = filename.lower()
    for sub in subfolders:
        folder = os.path.join(base_dir, *sub) if sub else base_dir
        if not os.path.isdir(folder):
            continue
        try:
            entries = os.listdir(folder)
        except OSError:
            continue
        for f in entries:
            if f.lower() == target:
                return os.path.join(folder, f)
    return None


def _load_photo(base_dir, filename, target_w, target_h, label=""):
    import traceback
    from PIL import Image, ImageTk
    import os

    img_path = os.path.join(base_dir, "src", "images", filename)

    print(f"Loading image from: {img_path}")

    if not os.path.exists(img_path):
        print(f"Image not found: {img_path}")
        return None

    try:
        img = Image.open(img_path).convert("RGB")

        # Convert float to int
        target_w = int(round(target_w))
        target_h = int(round(target_h))

        if target_w < 1:
            target_w = 1
        if target_h < 1:
            target_h = 1

        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(img)

        print(f"Loaded {filename} ({target_w} x {target_h})")

        return photo

    except Exception:
        traceback.print_exc()
        return None


class RackArea:

    def __init__(self, parent, fonts, hint_var: tk.StringVar):
        self._fonts    = fonts
        self._hint_var = hint_var
        self._selected = None
        self._slot_data: dict = {}

        right = tk.Frame(parent, bg=T["win_bg"])
        right.pack(side="left", fill="both", expand=True, padx=0, pady=10)

        self._canvas = tk.Canvas(
            right,
            bg=T["win_bg"],
            bd=0,
            highlightthickness=0,
        )
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", lambda e: self.draw())

        hint_bar = tk.Frame(right, bg=T["win_bg"])
        hint_bar.pack(fill="x", pady=(6, 0))

        hint_icon = tk.Label(
            hint_bar,
            text="ℹ",
            font=tkfont.Font(family="Segoe UI", size=10),
            bg=T["win_bg"],
            fg=T["accent"],
        )
        hint_icon.pack(side="left", padx=(6, 4))

        tk.Label(
            hint_bar,
            textvariable=hint_var,
            font=tkfont.Font(family="Segoe UI", size=10),
            bg=T["win_bg"],
            fg=T["text_hint"],
            cursor="hand2",
        ).pack(side="left")

    # ── Public ──────────────────────────────────────────────────────

    def clear(self):
        self._slot_data.clear()
        self._selected = None
        self.draw()

    def get_slot_data(self) -> dict:
        return dict(self._slot_data)

    def save_configuration(self, name: str = None):
        """Save current rack configuration to local system."""
        import json
        import datetime
        from tkinter import filedialog, messagebox

        if not name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"rack_config_{timestamp}.json"
        else:
            default_name = f"{name}.json"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self._canvas
        )

        if file_path:
            try:
                config = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "slot_data": self._slot_data,
                    "slot_count": SLOT_COUNT
                }
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Save Configuration", f"Configuration saved to {file_path}", parent=self._canvas)
                return file_path
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save configuration: {e}", parent=self._canvas)
                return None
        return None

    def load_configuration(self):
        """Load rack configuration from local system."""
        import json
        from tkinter import filedialog, messagebox

        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self._canvas
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)

                self._slot_data.clear()
                self._slot_data.update(config.get("slot_data", {}))
                self._selected = None
                self.draw()
                messagebox.showinfo("Load Configuration", f"Configuration loaded from {file_path}", parent=self._canvas)
                return config
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration: {e}", parent=self._canvas)
                return None
        return None

    # ── Layout constants ────────────────────────────────────────────

    def _layout(self, W: int, H: int) -> dict:
        PSM_W   = 140  # ← Increased width for PSM (0-index) column images
        PAD_X   = 14
        TOP_Y   = 32
        PAD_BOT = 10
        SHELL_H = H - TOP_Y - PAD_BOT

        slot_x0      = PAD_X + PSM_W + 8
        slot_w_total = W - PAD_X * 2 - PSM_W - 8 - PAD_X
        sw           = slot_w_total / SLOT_COUNT

        return dict(
            PAD_X=PAD_X, TOP_Y=TOP_Y, PAD_BOT=PAD_BOT,
            SHELL_H=SHELL_H, PSM_W=PSM_W,
            slot_x0=slot_x0, sw=sw,
            W=W, H=H,
        )

    # ── Main draw ───────────────────────────────────────────────────

    def draw(self):
        c = self._canvas
        c.delete("all")
        W = c.winfo_width()
        H = c.winfo_height()
        if W < 200 or H < 120:
            return

        L = self._layout(W, H)
        self._draw_rack_shell(c, L)
        self._draw_slot_headers(c, L)
        self._draw_psm_top(c, L)
        self._draw_psm_bottom(c, L)

        skip_next = False
        for slot in range(SLOT_COUNT):
            if skip_next:
                skip_next = False
                continue
            slot_num = slot + 1
            key      = f"0_{slot_num}"
            module   = self._slot_data.get(key)
            if module == DIS_MODULE:
                self._draw_dis_module(c, L, slot)
                skip_next = True
            else:
                self._draw_slot(c, L, slot)

    # ── Rack shell ──────────────────────────────────────────────────

    def _draw_rack_shell(self, c: tk.Canvas, L: dict):
        x1 = L["PAD_X"]
        y1 = L["TOP_Y"] - 6
        x2 = L["W"] - L["PAD_X"]
        y2 = y1 + L["SHELL_H"]

        c.create_rectangle(x1, y1, x2, y2,
                            fill=T["rack_shell_bot"],
                            outline="",
                            width=0, tags="rack_bg")
        c.create_rectangle(x1+6, y1+6, x2-6, y2-6,
                            fill=T["rack_row"],
                            outline="#0a0f18",
                            width=1, tags="rack_bg")

    # ── Slot number headers ─────────────────────────────────────────

    def _draw_slot_headers(self, c: tk.Canvas, L: dict):
        skip_next = False
        for i in range(1, SLOT_COUNT + 1):
            if skip_next:
                skip_next = False
                continue

            if i == 1:
                continue

            key    = f"0_{i}"
            module = self._slot_data.get(key)
            is_selected = (self._selected == key)

            fill_color = "#cc2222" if is_selected else "#888888"
            display_num = i - 1

            if module == DIS_MODULE:
                # DIS occupies raw slots i and i+1 (displayed numbers
                # i-1 and i respectively). Show the pair's SECOND /
                # higher displayed number — i.e. "i" — not the first
                # slot's own number (display_num = i-1).
                cx = L["slot_x0"] + (i - 1 + 1.0) * L["sw"]
                c.create_text(cx, L["TOP_Y"] - 14,
                              text=str(i),
                              font=self._fonts["num"],
                              fill=fill_color,
                              anchor="center")
                skip_next = True
            else:
                cx = L["slot_x0"] + (i - 1 + 0.5) * L["sw"]
                c.create_text(cx, L["TOP_Y"] - 14,
                              text=str(display_num),
                              font=self._fonts["num"],
                              fill=fill_color,
                              anchor="center")

    # ── Helper: draw one PSM panel (fallback, hand-drawn) ────────────

    def _draw_psm_panel(self, c: tk.Canvas, L: dict,
                        px1: int, py1: int, px2: int, py2: int,
                        label: str):
        mx = (px1 + px2) // 2

        c.create_rectangle(px1, py1, px2, py2,
                            fill=T["psm_body"],
                            outline=T["slot_edge_sh"],
                            width=2)
        c.create_line(px1, py1, px2, py1, fill="#2a4060", width=1)
        c.create_line(px1, py1, px1, py2, fill="#1e3050", width=1)

        logo_cx = mx
        logo_cy = py1 + 14
        logo_r  = 10
        c.create_oval(logo_cx - logo_r, logo_cy - logo_r,
                      logo_cx + logo_r, logo_cy + logo_r,
                      fill="#1a5fa0", outline="#4a9fd0", width=1)
        for ang in range(0, 180, 45):
            x0 = logo_cx + logo_r * math.cos(math.radians(ang))
            y0 = logo_cy + logo_r * math.sin(math.radians(ang))
            x1b = logo_cx - logo_r * math.cos(math.radians(ang))
            y1b = logo_cy - logo_r * math.sin(math.radians(ang))
            c.create_line(x0, y0, x1b, y1b, fill="#4ab0e0", width=1)
        c.create_oval(logo_cx - logo_r, logo_cy - 3,
                      logo_cx + logo_r, logo_cy + 3,
                      outline="#4ab0e0", width=1, fill="")

        strip_y = logo_cy + logo_r + 2
        c.create_rectangle(px1, strip_y, px2, strip_y + 14,
                            fill=T["psm_brand"], outline="")
        c.create_text(mx, strip_y + 7,
                      text="Sarayu",
                      font=tkfont.Font(family="Segoe UI", size=8, weight="bold",
                                       slant="italic"),
                      fill="#ffffff", anchor="center")

        vy = strip_y + 18
        for i, word in enumerate(["Vibration", "Monitoring", "System"]):
            c.create_text(mx, vy + i * 11,
                          text=word,
                          font=tkfont.Font(family="Segoe UI", size=6),
                          fill=T["psm_label"],
                          anchor="center")

        volts = ["+5V", "+12V", "-12V", "+24V", "-24V"]
        led_colors = [T["led_green"]] * 5
        vled_y0 = vy + 36
        lx = px1 + 6
        for i, (lbl, col) in enumerate(zip(volts, led_colors)):
            ly = vled_y0 + i * 12
            c.create_oval(lx-1, ly-1, lx+7, ly+7,
                          fill=col, outline="", stipple="gray50")
            c.create_oval(lx+1, ly+1, lx+5, ly+5,
                          fill=col, outline="#ffffff", width=1)
            c.create_text(lx + 10, ly + 3,
                          text=lbl,
                          font=tkfont.Font(family="Courier New", size=5),
                          fill="#8ab8d8",
                          anchor="w")

        num_y = vled_y0 + len(volts) * 12 + 6
        c.create_text(mx, num_y,
                      text="3000",
                      font=tkfont.Font(family="Segoe UI", size=14, weight="bold"),
                      fill=T["psm_3000"],
                      anchor="center")

        c.create_rectangle(px1+4, py2-20, px2-4, py2-4,
                            fill=T["psm_plate"],
                            outline="#1e3050")
        c.create_text(mx, py2-12,
                      text=label,
                      font=tkfont.Font(family="Segoe UI", size=6, weight="bold"),
                      fill=T["psm_plate_text"],
                      anchor="center")

        return num_y + 16

    # ── TOP PSM panel — Powersupply.jpg image, stretch-filled ───────

    def _draw_psm_top(self, c: tk.Canvas, L: dict):
        x1      = L["PAD_X"] + 14
        y1      = L["TOP_Y"] + 2
        x2      = x1 + L["PSM_W"] - 4
        top_end = L["TOP_Y"] + int(L["SHELL_H"] * 0.50)

        panel_w = max(1, x2 - x1)
        panel_h = max(1, top_end - y1)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        photo = _load_photo(base_dir, "Powersupply.jpg", panel_w, panel_h, label="PSM top")

        if not hasattr(self, '_psm_top_photo'):
            self._psm_top_photo = None

        if photo is not None:
            c.create_rectangle(x1, y1, x2, top_end,
                               fill="#0a0e14", outline="", tags="rack_bg")
            c.create_image(x1, y1, image=photo, anchor="nw")
            self._psm_top_photo = photo
        else:
            self._draw_psm_panel(c, L, x1, y1, x2, top_end, "VMS-3000 PSM")

    # ── MIDDLE strip — Powersupply.jpg image, stretch-filled ─────────────

    def _draw_psm_middle(self, c: tk.Canvas, L: dict):
        x1      = L["PAD_X"] + 14
        x2      = x1 + L["PSM_W"] - 4
        top_end = L["TOP_Y"] + int(L["SHELL_H"] * 0.45)
        bot_st  = L["TOP_Y"] + int(L["SHELL_H"] * 0.55)
        if bot_st - top_end < 10:
            bot_st = top_end + 10

        panel_w = max(1, x2 - x1)
        panel_h = max(1, bot_st - top_end)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        photo = _load_photo(base_dir, "Configuration_Module.jpg", panel_w, panel_h, label="PSM middle")

        if not hasattr(self, '_psm_middle_photo'):
            self._psm_middle_photo = None

        if photo is not None:
            c.create_rectangle(x1, top_end + 2, x2, bot_st - 2,
                               fill="#0a0e14", outline="", tags="rack_bg")
            c.create_image(x1, top_end + 2, image=photo, anchor="nw")
            self._psm_middle_photo = photo
        else:
            c.create_rectangle(x1, top_end + 2, x2, bot_st - 2,
                               fill="#0d1a28", outline="", tags="rack_bg")

    # ── BOTTOM PSM / CPU panel — Powersupply.jpg image, stretch-filled ───────

    def _draw_psm_bottom(self, c: tk.Canvas, L: dict):
        x1    = L["PAD_X"] + 14
        x2    = x1 + L["PSM_W"] - 4
        bot_st = L["TOP_Y"] + int(L["SHELL_H"] * 0.50)
        y2     = L["TOP_Y"] + L["SHELL_H"] - 12

        panel_w = max(1, x2 - x1)
        panel_h = max(1, y2 - bot_st)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        photo = _load_photo(base_dir, "Powersupply.jpg", panel_w, panel_h, label="PSM bottom")

        if not hasattr(self, '_psm_bottom_photo'):
            self._psm_bottom_photo = None

        if photo is not None:
            c.create_rectangle(x1, bot_st, x2, y2,
                               fill="#0a0e14", outline="", tags="rack_bg")
            c.create_image(x1, bot_st, image=photo, anchor="nw")
            self._psm_bottom_photo = photo
        else:
            content_y = self._draw_psm_panel(c, L, x1, bot_st, x2, y2, "VMS-3000 CPU")

            box_x1 = x1 + 6
            box_x2 = x2 - 6
            box_y1 = content_y
            box_y2 = box_y1 + 30
            c.create_rectangle(box_x1, box_y1, box_x2, box_y2,
                               fill="#0a1520", outline="#1e3050")

            status_leds = [
                ("PSM",  T["led_green"],  0, 0),
                ("TuRn", T["led_amber"],  0, 1),
                ("TIS",  T["led_red"],    1, 0),
                ("CMFD", T["led_blue"],   1, 1),
            ]
            cell_w = (box_x2 - box_x1) // 2
            cell_h = (box_y2 - box_y1) // 2
            for lbl, col, row, col_i in status_leds:
                cx_led = box_x1 + col_i * cell_w + 5
                cy_led = box_y1 + row  * cell_h + 8
                c.create_oval(cx_led, cy_led, cx_led+6, cy_led+6,
                              fill=col, outline="#ffffff", width=1)
                c.create_text(cx_led + 9, cy_led + 3,
                              text=lbl,
                              font=tkfont.Font(family="Courier New", size=5),
                              fill="#8ab8d8",
                              anchor="w")

            run_y = box_y2 + 6
            mx = (box_x1 + box_x2) // 2
            c.create_oval(mx-10, run_y, mx+10, run_y+12,
                          fill="#183018", outline="#1e3050", width=2)
            c.create_oval(mx-6,  run_y+2, mx+6,  run_y+10,
                          fill=T["led_green"], outline="#ffffff", width=1)
            c.create_text(mx, run_y + 18,
                          text="RUN",
                          font=tkfont.Font(family="Courier New", size=5, weight="bold"),
                          fill="#4af04a",
                          anchor="center")

            db9_y = run_y + 26
            db9_x1 = mx - 14
            db9_x2 = mx + 14
            db9_h  = 18
            c.create_rectangle(db9_x1, db9_y, db9_x2, db9_y + db9_h,
                               fill="#1a2a3a", outline="#3a5a7a", width=1)
            pin_rows = [5, 4]
            pr_y = db9_y + 4
            for npins in pin_rows:
                spacing = (db9_x2 - db9_x1 - 6) / max(npins - 1, 1)
                for p in range(npins):
                    px = db9_x1 + 3 + int(p * spacing)
                    c.create_oval(px, pr_y, px+3, pr_y+3,
                                  fill="#000000", outline="#5a7a9a", width=1)
                pr_y += 7
            c.create_text(mx, db9_y + db9_h + 6,
                          text="PROG",
                          font=tkfont.Font(family="Courier New", size=5),
                          fill="#6a9aba",
                          anchor="center")

            bar_y = db9_y + db9_h + 14
            bar_x1 = mx - 12
            bar_x2 = mx + 12
            bar_h  = 22
            c.create_rectangle(bar_x1, bar_y, bar_x2, bar_y + bar_h,
                               fill="#1a0000", outline="#3a0000", width=1)
            seg_count = 8
            seg_h = (bar_h - 4) / seg_count
            for seg in range(seg_count):
                intensity = "#ff0000" if seg < 5 else "#660000"
                sy = bar_y + 2 + int(seg * seg_h)
                c.create_rectangle(bar_x1+3, sy,
                                   bar_x2-3, sy + max(1, int(seg_h)-1),
                                   fill=intensity, outline="")

    # ══════════════════════════════════════════════════════════════════
    #  3000/12M/DIS — double-wide Measurement Module card
    # ══════════════════════════════════════════════════════════════════

    def _draw_dis_module(self, c: tk.Canvas, L: dict, slot_idx: int):
        slot_num = slot_idx + 1
        key      = f"0_{slot_num}"
        tag      = f"s_{key}"
        is_sel   = (self._selected == key)

        sw   = L["sw"]
        sx1  = int(L["slot_x0"] + slot_idx * sw + 3)
        sx2  = int(L["slot_x0"] + (slot_idx + 2) * sw - 6)
        sy1  = L["TOP_Y"] + 2
        sy2  = L["TOP_Y"] + L["SHELL_H"] - 12

        card_w = max(1, sx2 - sx1)
        card_h = max(1, sy2 - sy1)

        base_dir = os.path.dirname(os.path.abspath(__file__))

        if not hasattr(self, '_module_images'):
            self._module_images = {}

        photo = _load_photo(base_dir, "Measurement_Module.jpg", card_w, card_h,
                             label=f"DIS module slot {slot_num}")

        if photo is not None:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#0a0e14", outline="",
                               width=0, tags=tag)
            c.create_image(sx1, sy1, image=photo, anchor="nw", tags=tag)
            self._module_images[key] = photo
        else:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#1a4fa0", outline="",
                               width=0, tags=tag)
            mx = (sx1 + sx2) // 2
            my = (sy1 + sy2) // 2
            c.create_text(mx, my - 8,
                          text="VMS-3000",
                          fill="#ffffff",
                          font=tkfont.Font(family="Segoe UI", size=9, weight="bold"),
                          anchor="center", tags=tag)
            c.create_text(mx, my + 8,
                          text="3000/12M/DIS",
                          fill="#aaccff",
                          font=tkfont.Font(family="Segoe UI", size=7),
                          anchor="center", tags=tag)

        if is_sel:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="", outline="#f0b040",
                               width=3, tags=tag)

        c.tag_bind(tag, "<Enter>",
                   lambda e, t=tag, k=key: self._hover(t, k, True))
        c.tag_bind(tag, "<Leave>",
                   lambda e, t=tag, k=key: self._hover(t, k, False))
        c.tag_bind(tag, "<Button-1>",
                   lambda e, k=key, s=slot_num: self._click(k, s, e))
        c.tag_bind(tag, "<Button-3>",
                   lambda e, k=key, s=slot_num: self._right_click(k, s, e))

    # ── Slot card ────────────────────────────────────────────────────

    def _draw_slot(self, c: tk.Canvas, L: dict, slot_idx: int):
        slot_num = slot_idx + 1
        key      = f"0_{slot_num}"
        tag      = f"s_{key}"
        is_sel   = (self._selected == key)
        module   = self._slot_data.get(key)

        if _is_relay_module(module):
            self._draw_relay_module(c, L, slot_idx, module, is_sel, tag)
            return

        if _is_6m_module(module):
            self._draw_6m_module(c, L, slot_idx, module, is_sel, tag)
            return

        if module and is_image_display_module(module):
            self._draw_detailed_module(c, L, slot_idx, module, is_sel, tag)
            return

        sw  = L["sw"]
        sx1 = L["slot_x0"] + slot_idx * sw + 3
        sx2 = sx1 + sw - 6
        sy1 = L["TOP_Y"] + 2
        sy2 = L["TOP_Y"] + L["SHELL_H"] - 12
        slot_w = max(1, sx2 - sx1)
        slot_h = max(1, sy2 - sy1)
        mx  = (sx1 + sx2) // 2

        base_dir = os.path.dirname(os.path.abspath(__file__))

        if not hasattr(self, '_no_module_images'):
            self._no_module_images = {}

        # Slot 1 is the fixed Configuration/status panel (RUN dial, DB9 port,
        # DIP switches, LEDs) — it never shows the generic empty-slot
        # placeholder, it always shows Configuration_Module.jpg, matching
        # the physical rack.
        if slot_num == 1:
            photo = _load_photo(base_dir, "Configuration_Module.jpg", slot_w, slot_h,
                                 label=f"configuration panel slot {slot_num}")
        else:
            photo = _load_photo(base_dir, "NO_Module.jpg", slot_w, slot_h,
                                 label=f"empty slot {slot_num}")

        if photo is not None:
            # Draw image directly without black background
            c.create_image(sx1, sy1, image=photo, anchor="nw", tags=tag)
            # Store reference to prevent garbage collection
            self._no_module_images[key] = photo
        else:
            # Fallback to original blue rectangle if image fails to load
            if is_sel:
                face_col = T["slot_sel_face"]
                edge_col = T["slot_sel"]
            else:
                face_col = T["slot_face"]
                edge_col = T["slot_edge_sh"]

            c.create_rectangle(sx1, sy1, sx2, sy2,
                                fill=face_col,
                                outline=edge_col,
                                width=2,
                                tags=tag)

            cap_w = 22
            cap_h = 8
            c.create_rectangle(mx - cap_w // 2, sy1 + 8,
                                mx + cap_w // 2, sy1 + 8 + cap_h,
                                fill=T["slot_cap"] if not is_sel else "#fde68a",
                                outline=edge_col,
                                width=1, tags=tag)

            panel_y1 = sy1 + 8 + cap_h + 8
            panel_y2 = sy2 - 10
            c.create_rectangle(sx1 + 6, panel_y1, sx2 - 6, panel_y2,
                                fill=face_col,
                                outline=edge_col,
                                width=1, tags=tag)

            if module:
                short = module.split()[0]
                c.create_text(mx, (panel_y1 + panel_y2) // 2,
                              text=short,
                              font=tkfont.Font(family="Courier New", size=7, weight="bold"),
                              fill=T["slot_mod_fg"],
                              anchor="center",
                              tags=tag)

            c.create_rectangle(sx1 + 4, sy2 - 6, sx2 - 4, sy2 - 2,
                                fill="#0a1520",
                                outline="",
                                tags=tag)

        # Draw selection outline if selected
        if is_sel:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="", outline="#f0b040",
                               width=3, tags=tag)

        c.tag_bind(tag, "<Enter>",
                   lambda e, t=tag, k=key: self._hover(t, k, True))
        c.tag_bind(tag, "<Leave>",
                   lambda e, t=tag, k=key: self._hover(t, k, False))
        c.tag_bind(tag, "<Button-1>",
                   lambda e, k=key, s=slot_num: self._click(k, s, e))

    # ══════════════════════════════════════════════════════════════════
    #  VMM-6M detailed module — single-slot image card
    # ══════════════════════════════════════════════════════════════════

    def _draw_detailed_module(self, c: tk.Canvas, L: dict, slot_idx: int,
                              module: str, is_sel: bool, tag: str):
        slot_num = slot_idx + 1
        key      = f"0_{slot_num}"

        sw     = L["sw"]
        sx1    = int(L["slot_x0"] + slot_idx * sw + 3)
        sx2    = int(sx1 + sw - 6)
        sy1    = L["TOP_Y"] + 2
        sy2    = L["TOP_Y"] + L["SHELL_H"] - 12
        slot_w = max(1, sx2 - sx1)
        slot_h = max(1, sy2 - sy1)

        base_dir = os.path.dirname(os.path.abspath(__file__))

        if not hasattr(self, '_module_images'):
            self._module_images = {}

        photo = _load_photo(base_dir, "VMM-6M.jpg", slot_w, slot_h,
                             label=f"VMM-6M slot {slot_num}")

        if photo is not None:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#0a0e14", outline="",
                               width=0, tags=tag)
            c.create_image(sx1, sy1, image=photo, anchor="nw", tags=tag)
            self._module_images[key] = photo
        else:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#1a4fa0", outline="",
                               width=0, tags=tag)
            c.create_text((sx1 + sx2) // 2, (sy1 + sy2) // 2,
                          text="VMM-6M",
                          fill="#ffffff",
                          font=tkfont.Font(family="Segoe UI", size=8, weight="bold"),
                          anchor="center", tags=tag)

        if is_sel:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="", outline="#f0b040",
                               width=3, tags=tag)

        c.tag_bind(tag, "<Enter>",
                   lambda e, t=tag, k=key: self._hover(t, k, True))
        c.tag_bind(tag, "<Leave>",
                   lambda e, t=tag, k=key: self._hover(t, k, False))
        c.tag_bind(tag, "<Button-1>",
                   lambda e, k=key, s=slot_num: self._click(k, s, e))

    # ══════════════════════════════════════════════════════════════════
    #  3000/RLY — single-slot Relay module image card
    # ══════════════════════════════════════════════════════════════════

    def _draw_relay_module(self, c: tk.Canvas, L: dict, slot_idx: int,
                            module: str, is_sel: bool, tag: str):
        slot_num = slot_idx + 1
        key      = f"0_{slot_num}"

        sw     = L["sw"]
        sx1    = int(L["slot_x0"] + slot_idx * sw + 3)
        sx2    = int(sx1 + sw - 6)
        sy1    = L["TOP_Y"] + 2
        sy2    = L["TOP_Y"] + L["SHELL_H"] - 12
        slot_w = max(1, sx2 - sx1)
        slot_h = max(1, sy2 - sy1)

        base_dir = os.path.dirname(os.path.abspath(__file__))

        if not hasattr(self, '_module_images'):
            self._module_images = {}

        photo = _load_photo(base_dir, "Relay_Module.jpg", slot_w, slot_h,
                             label=f"Relay slot {slot_num}")

        if photo is not None:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#0a0e14", outline="",
                               width=0, tags=tag)
            c.create_image(sx1, sy1, image=photo, anchor="nw", tags=tag)
            self._module_images[key] = photo
        else:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#1a4fa0", outline="",
                               width=0, tags=tag)
            c.create_text((sx1 + sx2) // 2, (sy1 + sy2) // 2,
                          text="3000/RLY",
                          fill="#ffffff",
                          font=tkfont.Font(family="Segoe UI", size=8, weight="bold"),
                          anchor="center", tags=tag)

        if is_sel:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="", outline="#f0b040",
                               width=3, tags=tag)

        c.tag_bind(tag, "<Enter>",
                   lambda e, t=tag, k=key: self._hover(t, k, True))
        c.tag_bind(tag, "<Leave>",
                   lambda e, t=tag, k=key: self._hover(t, k, False))
        c.tag_bind(tag, "<Button-1>",
                   lambda e, k=key, s=slot_num: self._click(k, s, e))
        c.tag_bind(tag, "<Button-3>",
                   lambda e, k=key, s=slot_num: self._right_click(k, s, e))

    # ══════════════════════════════════════════════════════════════════
    #  3000/6M — single-slot 6M module image card
    # ══════════════════════════════════════════════════════════════════

    def _draw_6m_module(self, c: tk.Canvas, L: dict, slot_idx: int,
                       module: str, is_sel: bool, tag: str):
        slot_num = slot_idx + 1
        key      = f"0_{slot_num}"

        sw     = L["sw"]
        sx1    = int(L["slot_x0"] + slot_idx * sw + 3)
        sx2    = int(sx1 + sw - 6)
        sy1    = L["TOP_Y"] + 2
        sy2    = L["TOP_Y"] + L["SHELL_H"] - 12
        slot_w = max(1, sx2 - sx1)
        slot_h = max(1, sy2 - sy1)

        base_dir = os.path.dirname(os.path.abspath(__file__))

        if not hasattr(self, '_6m_images'):
            self._6m_images = {}

        photo = _load_photo(base_dir, "VMM-6M.jpg", slot_w, slot_h,
                             label=f"6M slot {slot_num}")

        if photo is not None:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#0a0e14", outline="",
                               width=0, tags=tag)
            c.create_image(sx1, sy1, image=photo, anchor="nw", tags=tag)
            self._6m_images[key] = photo
        else:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#5a8a5a", outline="",
                               width=0, tags=tag)
            c.create_text((sx1 + sx2) // 2, (sy1 + sy2) // 2,
                          text="3000/6M",
                          fill="#ffffff",
                          font=tkfont.Font(family="Segoe UI", size=8, weight="bold"),
                          anchor="center", tags=tag)

        if is_sel:
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="", outline="#f0b040",
                               width=3, tags=tag)

        c.tag_bind(tag, "<Enter>",
                   lambda e, t=tag, k=key: self._hover(t, k, True))
        c.tag_bind(tag, "<Leave>",
                   lambda e, t=tag, k=key: self._hover(t, k, False))
        c.tag_bind(tag, "<Button-1>",
                   lambda e, k=key, s=slot_num: self._click(k, s, e))
        c.tag_bind(tag, "<Button-3>",
                   lambda e, k=key, s=slot_num: self._right_click(k, s, e))

    # ── Interaction ─────────────────────────────────────────────────

    def _hover(self, tag: str, key: str, entering: bool):
        if self._selected == key:
            return
        slot_n   = key.split("_")[1]
        assigned = self._slot_data.get(key)
        if entering:
            self._hint_var.set(
                f"Slot {slot_n}  —  "
                + (f"Module: {assigned}" if assigned else "Empty — click to assign module")
            )
        else:
            self._hint_var.set("Click any slot to assign module")

    def _click(self, key: str, slot_num: int, event=None):
        self._selected = key
        self.draw()
        self._hint_var.set(f"Slot {slot_num} selected")

        if slot_num == 1:
            self._config_settings_dialog()
        else:
            self._module_dialog(key, slot_num, event)

    def _right_click(self, key: str, slot_num: int, event):
        """Handle right-click on DIS_MODULE and RELAY_MODULE to show context menu."""
        module = self._slot_data.get(key)

        # Show context menu for DIS_MODULE with Options, Setpoints, Point Names
        if module == DIS_MODULE:
            def on_options(slot):
                dialog = ProximityMonitor3000ConfigDialog(self._canvas, slot)
                dialog.show()

            def on_setpoints(slot):
                dialog = SetpointsDialog(self._canvas, self._fonts, slot)
                dialog.show()

            def on_point_names(slot):
                # TODO: Implement Point Names dialog
                print(f"Point Names for slot {slot}")

            context_menu = PointOptionsContextMenu(
                self._canvas,
                self._fonts,
                slot_num,
                on_options=on_options,
                on_setpoints=on_setpoints,
                on_point_names=on_point_names
            )

            # Get screen coordinates for the menu
            x = event.x_root
            y = event.y_root
            context_menu.show(x, y)

        # Show context menu for RELAY_MODULE with only Setpoints
        elif _is_relay_module(module):
            def on_setpoints(slot):
                dialog = RelayConfigDialog(self._canvas, slot, module, "A1", rack_config=self._slot_data)
                dialog.show()

            context_menu = PointOptionsContextMenu(
                self._canvas,
                self._fonts,
                slot_num,
                on_setpoints=on_setpoints
            )

            # Get screen coordinates for the menu
            x = event.x_root
            y = event.y_root
            context_menu.show(x, y)

        # Show context menu for 3000/6M with Options, Setpoints, Point Names
        elif _is_6m_module(module):
            def on_options(slot):
                dialog = SixMOptionsDialog(self._canvas, slot)
                dialog.show()

            def on_setpoints(slot):
                # Reuse the exact same Setpoints dialog design as 3000/12M/DIS
                dialog = SetpointsDialog(self._canvas, self._fonts, slot)
                dialog.show()

            def on_point_names(slot):
                # TODO: Implement 3000/6M Point Names dialog
                print(f"Point Names for 3000/6M slot {slot}")

            context_menu = PointOptionsContextMenu(
                self._canvas,
                self._fonts,
                slot_num,
                on_options=on_options,
                on_setpoints=on_setpoints,
                on_point_names=on_point_names
            )

            # Get screen coordinates for the menu
            x = event.x_root
            y = event.y_root
            context_menu.show(x, y)

    # ── Configuration Settings dialog (for slot 1) ──────────────────

    def _config_settings_dialog(self):
        popup = ConfigurationSettingsPopup(self._canvas, self._fonts)
        popup.show()
        self._selected = None
        self.draw()
        self._hint_var.set("Configuration Settings closed")

    # ── Module assignment — cascading flyout menu ────────────────────

    # Raw slots where a DIS module may start. DIS occupies (slot_num,
    # slot_num+1) — a sliding window, NOT fixed non-overlapping pairs.
    # Any raw slot from 2 up to SLOT_COUNT-1 is a valid start: raw slot 1
    # is reserved for Configuration Settings. Raw slot SLOT_COUNT (the
    # last physical slot, displayed as "11") CAN become the tail of a DIS
    # pair — e.g. displayed slot 10 (raw 11) pairing with displayed slot
    # 11 (raw 12) is valid and shows 3000/12M/DIS across both. The
    # "6M/Relay only" restriction below only applies when the last slot
    # is selected directly on its own, not when it's filled as the tail
    # of a DIS pair started from the slot before it.
    _DIS_ALLOWED_START_SLOTS = tuple(range(2, SLOT_COUNT))
    # Raw slot 12 (displayed as "11") is the last physical slot. If it is
    # selected directly (not as the tail of a DIS pair from raw slot 11),
    # only 3000/6M or Relay are permitted there.
    _LAST_SLOT_RESTRICTED = 12

    @staticmethod
    def _is_vmm_or_relay(selection: str) -> bool:
        if not selection:
            return False
        if selection == "No Modules":
            return True
        if selection == VMM_MODULE or selection == "3000/6M":
            return True
        return _is_relay_module(selection)

    def _module_dialog(self, key: str, slot_num: int, event=None):
        def on_selection(selection):
            current_module = self._slot_data.get(key)

            # ── Rule: last slot (raw 12 / displayed 11) is restricted ──
            if slot_num == self._LAST_SLOT_RESTRICTED and not self._is_vmm_or_relay(selection):
                from tkinter import messagebox
                messagebox.showwarning(
                    "Module Selection",
                    "This slot only allows 3000/6M or Relay modules.",
                    parent=self._canvas
                )
                return

            # ── Rule: even slot that's the tail of a DIS pair ──
            prev_slot_key = f"0_{slot_num - 1}"
            prev_module = self._slot_data.get(prev_slot_key)
            if prev_module == DIS_MODULE and selection != "No Modules":
                from tkinter import messagebox
                messagebox.showwarning(
                    "Module Selection",
                    f"This slot is occupied by 3000/12M/DIS from the previous slot.\n"
                    "Please select a different slot.",
                    parent=self._canvas
                )
                return

            # ── Rule: DIS placement — only allowed start slots, and its
            #    partner slot must be free and not the restricted last slot ──
            if selection == DIS_MODULE:
                if slot_num not in self._DIS_ALLOWED_START_SLOTS:
                    from tkinter import messagebox
                    messagebox.showwarning(
                        "Module Selection",
                        "3000/12M/DIS cannot be placed starting at this slot.",
                        parent=self._canvas
                    )
                    return

                partner_num = slot_num + 1
                partner_key = f"0_{partner_num}"
                partner_module = self._slot_data.get(partner_key)
                # Allow DIS if partner slot is empty (None) or "No Modules"
                if partner_module is not None and partner_module != "No Modules":
                    from tkinter import messagebox
                    messagebox.showwarning(
                        "Module Selection",
                        "The next slot is already occupied.\n"
                        "3000/12M/DIS needs this slot and the next one to be free.",
                        parent=self._canvas
                    )
                    return

            if current_module and selection != "No Modules" and current_module != selection:
                def on_switch_confirmed(confirmed):
                    if confirmed:
                        if selection == "No Modules":
                            self._slot_data.pop(key, None)
                        else:
                            self._slot_data[key] = selection
                        self._selected = key
                        self.draw()
                        self._hint_var.set(
                            f"Slot {slot_num} → {self._slot_data.get(key, 'Empty')}"
                        )

                popup = ModuleSwitchConfirmationPopup(
                    self._canvas, self._fonts, current_module, selection, on_switch_confirmed
                )
                popup.show()
                return

            if selection == "No Modules":
                self._slot_data.pop(key, None)
            else:
                self._slot_data[key] = selection
            self._selected = key
            self.draw()
            self._hint_var.set(
                f"Slot {slot_num} → {self._slot_data.get(key, 'Empty')}"
            )

        # Cascading flyout menu (Monitors ▸ Proximeter/Tachometer ▸ Model,
        # Gateways, Relay ▸ Model, No Modules) — replaces the old card-style
        # ModuleSelectionPopup dialog.
        menu = CascadingMenu(self._canvas, self._fonts, on_selection)

        if event is not None:
            x, y = event.x_root, event.y_root
        else:
            # Fallback: anchor near the canvas if no click event is available
            x = self._canvas.winfo_rootx() + 40
            y = self._canvas.winfo_rooty() + 40

        menu.show_menu(x, y)