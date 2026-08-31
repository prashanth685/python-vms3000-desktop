"""
connection.py — VMS 3000  •  Connection Dialogs
Theme-matched to the industrial SCADA palette (navy/steel/amber/teal).
All colours, fonts, sizes and highlights come directly from T{}.
Single self-contained file — no external theme.py required.
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox


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
#  DIRECT CONNECT DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class DirectConnectDialog:
    """
    Direct Connect dialog — VMS 3000 SCADA theme.
    
    Allows direct connection to rack device via serial/USB.
    """

    def __init__(self, parent, fonts):
        self._fonts  = fonts
        self._parent = parent
        self._dialog = None
        self._vars   = {}

        self._defaults = {
            "connect_password": "",
            "rack_address": "1",
            "com_port": "COM1",
            "baud_rate": "9600",
        }

        self._create_dialog()

    def _f(self, key, family="Segoe UI", size=9, weight="normal"):
        return self._fonts.get(key, tkfont.Font(family=family, size=size, weight=weight))

    def _create_dialog(self):
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title("Direct Connect")
        self._dialog.configure(bg=T["win_bg"])
        self._dialog.resizable(False, False)
        self._dialog.grab_set()

        # Titlebar strip (navy)
        self._create_titlebar()

        # Teal accent rule under titlebar
        tk.Frame(self._dialog, bg=T["accent_teal"], height=3).pack(fill="x")

        # Body
        body = tk.Frame(self._dialog, bg=T["win_bg"], padx=16, pady=12)
        body.pack(fill="both", expand=True)

        self._create_connection_group(body)

        # Button strip
        self._create_buttons()

        # Size & centre
        self._dialog.update_idletasks()
        w, h = 450, 320
        sw = self._dialog.winfo_screenwidth()
        sh = self._dialog.winfo_screenheight()
        self._dialog.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _create_titlebar(self):
        bar = tk.Frame(self._dialog, bg=T["titlebar"], pady=10)
        bar.pack(fill="x")

        tk.Label(
            bar,
            text="  Direct Connect",
            font=self._f("ui_b", size=11, weight="bold"),
            bg=T["titlebar"],
            fg=T["text_white"],
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        badge = tk.Label(
            bar,
            text="  VMS 3000  ",
            font=self._f("ui_b", size=10, weight="bold"),
            bg=T["accent_light"],
            fg=T["text_white"],
            relief="flat",
            padx=6,
            pady=4,
        )
        badge.pack(side="right", padx=(0, 12))

    def _group(self, parent, title):
        return tk.LabelFrame(
            parent,
            text=f"  {title}  ",
            font=self._f("sm_b", size=9, weight="bold"),
            bg=T["win_bg"],
            fg=T["accent"],
            bd=2,
            relief="groove",
            padx=14,
            pady=10,
        )

    def _create_connection_group(self, parent):
        grp = self._group(parent, "Connection Settings")
        grp.pack(fill="x", pady=(0, 10))

        self._field(grp, "Connect Password :", "connect_password", pw=True)
        self._field_with_browse(grp, "Rack Address :", "rack_address")
        self._field(grp, "COM Port :", "com_port", pw=False)
        self._field(grp, "Baud Rate :", "baud_rate", pw=False)

    def _field(self, parent, label_text, key, *, pw):
        row = tk.Frame(parent, bg=T["win_bg"])
        row.pack(fill="x", pady=4)

        lbl = tk.Label(
            row,
            text=label_text,
            font=self._f("sm_b", size=9, weight="bold"),
            bg=T["win_bg"],
            fg=T["text"],
            anchor="e",
            width=18,
        )
        lbl.pack(side="left")

        var = tk.StringVar(value=self._defaults.get(key, ""))
        self._vars[key] = var

        entry = tk.Entry(
            row,
            textvariable=var,
            font=self._f("mono", family="Consolas", size=10),
            bg="#ffffff",
            fg=T["text"],
            insertbackground=T["accent_teal"],
            selectbackground=T["accent_light"],
            selectforeground=T["text_white"],
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=T["btn_border"],
            highlightcolor=T["accent_teal"],
            width=18,
            show="*" if pw else "",
        )
        entry.pack(side="left", padx=(8, 0))

        def _on_enter(e):
            entry.config(highlightbackground=T["accent_light"])
        def _on_leave(e):
            entry.config(highlightbackground=T["btn_border"])

        entry.bind("<Enter>", _on_enter)
        entry.bind("<Leave>", _on_leave)

    def _field_with_browse(self, parent, label_text, key):
        """Field with Browse button for Rack Address."""
        row = tk.Frame(parent, bg=T["win_bg"])
        row.pack(fill="x", pady=4)

        lbl = tk.Label(
            row,
            text=label_text,
            font=self._f("sm_b", size=9, weight="bold"),
            bg=T["win_bg"],
            fg=T["text"],
            anchor="e",
            width=18,
        )
        lbl.pack(side="left")

        var = tk.StringVar(value=self._defaults.get(key, ""))
        self._vars[key] = var

        entry = tk.Entry(
            row,
            textvariable=var,
            font=self._f("mono", family="Consolas", size=10),
            bg="#ffffff",
            fg=T["text"],
            insertbackground=T["accent_teal"],
            selectbackground=T["accent_light"],
            selectforeground=T["text_white"],
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=T["btn_border"],
            highlightcolor=T["accent_teal"],
            width=10,
        )
        entry.pack(side="left", padx=(8, 4))

        def _on_enter(e):
            entry.config(highlightbackground=T["accent_light"])
        def _on_leave(e):
            entry.config(highlightbackground=T["btn_border"])

        entry.bind("<Enter>", _on_enter)
        entry.bind("<Leave>", _on_leave)

        # Browse button
        browse_btn = tk.Button(
            row,
            text="Browse…",
            command=self._on_browse_rack,
            font=self._f("sm", size=8),
            bg=T["btn_face"],
            fg=T["text"],
            activebackground=T["btn_hover"],
            activeforeground=T["text"],
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=T["btn_border"],
        )
        browse_btn.pack(side="left", padx=(0, 8))

        def _e(ev): browse_btn.config(bg=T["btn_hover"])
        def _l(ev): browse_btn.config(bg=T["btn_face"])
        browse_btn.bind("<Enter>", _e)
        browse_btn.bind("<Leave>", _l)

    def _on_browse_rack(self):
        """Browse for rack address - shows available rack addresses."""
        dlg = tk.Toplevel(self._dialog)
        dlg.title("Select Rack Address")
        dlg.configure(bg=T["win_bg"])
        dlg.resizable(False, False)
        dlg.geometry("300x400")
        dlg.transient(self._dialog)
        dlg.grab_set()

        # Titlebar
        hdr = tk.Frame(dlg, bg=T["titlebar"], pady=8)
        hdr.pack(fill="x")
        tk.Label(
            hdr, text="  Rack Addresses",
            font=self._f("ui_b", size=10, weight="bold"),
            bg=T["titlebar"], fg=T["text_white"], anchor="w",
        ).pack(fill="x")

        tk.Frame(dlg, bg=T["accent_teal"], height=3).pack(fill="x")

        # Body with list
        body = tk.Frame(dlg, bg=T["win_bg"], padx=12, pady=12)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Available Rack Addresses:",
            font=self._f("sm_b", size=9, weight="bold"),
            bg=T["win_bg"],
            fg=T["text"],
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        # Listbox with addresses
        list_frame = tk.Frame(body, bg=T["win_bg"])
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=T["btn_border"])
        scrollbar.pack(side="right", fill="y")

        addr_list = tk.Listbox(
            list_frame,
            font=self._f("mono", family="Consolas", size=9),
            bg="#ffffff",
            fg=T["text"],
            selectbackground=T["accent_light"],
            selectforeground=T["text_white"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=T["btn_border"],
            highlightcolor=T["accent_teal"],
            yscrollcommand=scrollbar.set,
            height=12,
        )
        addr_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=addr_list.yview)

        # Add addresses 1-255
        for i in range(1, 256):
            addr_list.insert(tk.END, f"Rack {i:03d}")

        # Select button
        def _on_select():
            selection = addr_list.curselection()
            if selection:
                addr = addr_list.get(selection[0])
                # Extract number from "Rack 001" format
                addr_num = addr.split()[1]
                self._vars["rack_address"].set(addr_num)
                dlg.destroy()

        btn_frame = tk.Frame(body, bg=T["win_bg"])
        btn_frame.pack(fill="x", pady=(12, 0))

        tk.Button(
            btn_frame,
            text="  Select  ",
            command=_on_select,
            font=self._f("ui_b", size=9, weight="bold"),
            bg=T["accent"],
            fg=T["text_white"],
            activebackground=T["accent_light"],
            activeforeground=T["text_white"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
        ).pack(side="right")

        tk.Button(
            btn_frame,
            text="  Cancel  ",
            command=dlg.destroy,
            font=self._f("ui_b", size=9, weight="bold"),
            bg=T["btn_face"],
            fg=T["text"],
            activebackground=T["btn_hover"],
            activeforeground=T["text"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
        ).pack(side="right", padx=(0, 8))

    def _create_buttons(self):
        strip = tk.Frame(
            self._dialog,
            bg=T["status_bg"],
            pady=12,
            relief="flat",
            bd=0,
        )
        tk.Frame(self._dialog, bg=T["status_border"], height=1).pack(fill="x")
        strip.pack(fill="x", padx=0)

        inner = tk.Frame(strip, bg=T["status_bg"])
        inner.pack(padx=16)

        ub = self._f("ui_b", size=9, weight="bold")

        def _btn(text, cmd, style="normal"):
            if style == "primary":
                bg  = T["accent"]
                fg  = T["text_white"]
                abg = T["accent_light"]
                afg = T["text_white"]
            else:
                bg  = T["btn_face"]
                fg  = T["text"]
                abg = T["btn_hover"]
                afg = T["text"]

            b = tk.Button(
                inner,
                text=f"  {text}  ",
                command=cmd,
                font=ub,
                bg=bg,
                fg=fg,
                activebackground=abg,
                activeforeground=afg,
                relief="flat",
                bd=0,
                padx=12,
                pady=6,
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=T["btn_border"],
            )
            b.pack(side="left", padx=(0, 8))

            def _e(ev): b.config(bg=abg, fg=afg)
            def _l(ev): b.config(bg=bg,  fg=fg)
            b.bind("<Enter>", _e)
            b.bind("<Leave>", _l)
            return b

        _btn("Connect", self._on_connect, style="primary")
        _btn("Browse", self._on_browse, style="normal")
        _btn("Cancel", self._on_cancel, style="normal")
        _btn("Help", self._on_help, style="normal")

    def _on_connect(self):
        saved = {k: v.get() for k, v in self._vars.items()}
        print("Direct Connect settings:")
        for k, v in saved.items():
            print(f"  {k}: {v}")
        messagebox.showinfo("Direct Connect", "Connecting to device...", parent=self._dialog)
        self._dialog.destroy()

    def _on_cancel(self):
        self._dialog.destroy()

    def _on_browse(self):
        """Browse for configuration file or device."""
        messagebox.showinfo("Browse", "Browse functionality for Direct Connect.", parent=self._dialog)

    def _on_help(self):
        """Show help for Direct Connect."""
        help_dlg = tk.Toplevel(self._dialog)
        help_dlg.title("Direct Connect — Help")
        help_dlg.configure(bg=T["win_bg"])
        help_dlg.resizable(False, False)
        help_dlg.geometry("450x350")
        help_dlg.transient(self._dialog)
        help_dlg.grab_set()

        # Titlebar
        hdr = tk.Frame(help_dlg, bg=T["titlebar"], pady=8)
        hdr.pack(fill="x")
        tk.Label(
            hdr, text="  Direct Connect Help",
            font=self._f("ui_b", size=10, weight="bold"),
            bg=T["titlebar"], fg=T["text_white"], anchor="w",
        ).pack(fill="x")

        tk.Frame(help_dlg, bg=T["accent_teal"], height=3).pack(fill="x")

        # Body
        body = tk.Frame(help_dlg, bg=T["win_bg"], padx=16, pady=12)
        body.pack(fill="both", expand=True)

        help_text = (
            "Connect Password\n"
            "    Password required to connect to the rack device.\n\n"
            "Rack Address\n"
            "    Unique address of the rack (1-255). Click Browse to select.\n\n"
            "COM Port\n"
            "    Serial port for direct connection (COM1-COM16).\n\n"
            "Baud Rate\n"
            "    Communication speed for serial connection.\n\n"
            "Click Connect to establish the connection."
        )

        tk.Label(
            body, text=help_text,
            font=self._f("sm", size=9),
            bg=T["win_bg"],
            fg=T["text"],
            justify="left", anchor="nw",
        ).pack(fill="both", expand=True)

        tk.Frame(body, bg=T["status_border"], height=1).pack(fill="x", pady=(10, 0))

        tk.Button(
            body, text="  Close  ", command=help_dlg.destroy,
            font=self._f("ui_b", size=9, weight="bold"),
            bg=T["accent"], fg=T["text_white"],
            activebackground=T["accent_light"],
            activeforeground=T["text_white"],
            relief="flat", bd=0,
            padx=12, pady=5,
            cursor="hand2",
        ).pack(pady=(10, 0))

    def show(self):
        self._dialog.wait_window()


# ══════════════════════════════════════════════════════════════════════════════
#  NETWORK CONNECT DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class NetworkConnectDialog:
    """
    Network Connect dialog — VMS 3000 SCADA theme.
    
    Allows network connection to rack device via TCP/IP.
    """

    def __init__(self, parent, fonts):
        self._fonts  = fonts
        self._parent = parent
        self._dialog = None
        self._vars   = {}

        self._defaults = {
            "connect_password": "",
            "rack_address": "1",
            "ip_address": "192.168.1.255",
            "port": "502",
        }

        self._create_dialog()

    def _f(self, key, family="Segoe UI", size=9, weight="normal"):
        return self._fonts.get(key, tkfont.Font(family=family, size=size, weight=weight))

    def _create_dialog(self):
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title("Network Connect")
        self._dialog.configure(bg=T["win_bg"])
        self._dialog.resizable(False, False)
        self._dialog.grab_set()

        # Titlebar strip (navy)
        self._create_titlebar()

        # Teal accent rule under titlebar
        tk.Frame(self._dialog, bg=T["accent_teal"], height=3).pack(fill="x")

        # Body
        body = tk.Frame(self._dialog, bg=T["win_bg"], padx=16, pady=12)
        body.pack(fill="both", expand=True)

        self._create_connection_group(body)

        # Button strip
        self._create_buttons()

        # Size & centre
        self._dialog.update_idletasks()
        w, h = 450, 320
        sw = self._dialog.winfo_screenwidth()
        sh = self._dialog.winfo_screenheight()
        self._dialog.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _create_titlebar(self):
        bar = tk.Frame(self._dialog, bg=T["titlebar"], pady=10)
        bar.pack(fill="x")

        tk.Label(
            bar,
            text="  Network Connect",
            font=self._f("ui_b", size=11, weight="bold"),
            bg=T["titlebar"],
            fg=T["text_white"],
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        badge = tk.Label(
            bar,
            text="  VMS 3000  ",
            font=self._f("ui_b", size=10, weight="bold"),
            bg=T["accent_light"],
            fg=T["text_white"],
            relief="flat",
            padx=6,
            pady=4,
        )
        badge.pack(side="right", padx=(0, 12))

    def _group(self, parent, title):
        return tk.LabelFrame(
            parent,
            text=f"  {title}  ",
            font=self._f("sm_b", size=9, weight="bold"),
            bg=T["win_bg"],
            fg=T["accent"],
            bd=2,
            relief="groove",
            padx=14,
            pady=10,
        )

    def _create_connection_group(self, parent):
        grp = self._group(parent, "Network Settings")
        grp.pack(fill="x", pady=(0, 10))

        self._field(grp, "IP Address :", "ip_address", pw=False)
        self._field(grp, "Port :", "port", pw=False)
        self._field(grp, "Timeout (sec) :", "timeout", pw=False)

    def _field(self, parent, label_text, key, *, pw):
        row = tk.Frame(parent, bg=T["win_bg"])
        row.pack(fill="x", pady=4)

        lbl = tk.Label(
            row,
            text=label_text,
            font=self._f("sm_b", size=9, weight="bold"),
            bg=T["win_bg"],
            fg=T["text"],
            anchor="e",
            width=18,
        )
        lbl.pack(side="left")

        var = tk.StringVar(value=self._defaults.get(key, ""))
        self._vars[key] = var

        entry = tk.Entry(
            row,
            textvariable=var,
            font=self._f("mono", family="Consolas", size=10),
            bg="#ffffff",
            fg=T["text"],
            insertbackground=T["accent_teal"],
            selectbackground=T["accent_light"],
            selectforeground=T["text_white"],
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=T["btn_border"],
            highlightcolor=T["accent_teal"],
            width=18,
            show="*" if pw else "",
        )
        entry.pack(side="left", padx=(8, 0))

        def _on_enter(e):
            entry.config(highlightbackground=T["accent_light"])
        def _on_leave(e):
            entry.config(highlightbackground=T["btn_border"])

        entry.bind("<Enter>", _on_enter)
        entry.bind("<Leave>", _on_leave)

    def _create_buttons(self):
        strip = tk.Frame(
            self._dialog,
            bg=T["status_bg"],
            pady=12,
            relief="flat",
            bd=0,
        )
        tk.Frame(self._dialog, bg=T["status_border"], height=1).pack(fill="x")
        strip.pack(fill="x", padx=0)

        inner = tk.Frame(strip, bg=T["status_bg"])
        inner.pack(padx=16)

        ub = self._f("ui_b", size=9, weight="bold")

        def _btn(text, cmd, style="normal"):
            if style == "primary":
                bg  = T["accent"]
                fg  = T["text_white"]
                abg = T["accent_light"]
                afg = T["text_white"]
            else:
                bg  = T["btn_face"]
                fg  = T["text"]
                abg = T["btn_hover"]
                afg = T["text"]

            b = tk.Button(
                inner,
                text=f"  {text}  ",
                command=cmd,
                font=ub,
                bg=bg,
                fg=fg,
                activebackground=abg,
                activeforeground=afg,
                relief="flat",
                bd=0,
                padx=12,
                pady=6,
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=T["btn_border"],
            )
            b.pack(side="left", padx=(0, 8))

            def _e(ev): b.config(bg=abg, fg=afg)
            def _l(ev): b.config(bg=bg,  fg=fg)
            b.bind("<Enter>", _e)
            b.bind("<Leave>", _l)
            return b

        _btn("Connect", self._on_connect, style="primary")
        _btn("Cancel", self._on_cancel, style="normal")

    def _on_connect(self):
        saved = {k: v.get() for k, v in self._vars.items()}
        print("Network Connect settings:")
        for k, v in saved.items():
            print(f"  {k}: {v}")
        messagebox.showinfo("Network Connect", "Connecting to device...", parent=self._dialog)
        self._dialog.destroy()

    def _on_cancel(self):
        self._dialog.destroy()

    def show(self):
        self._dialog.wait_window()


# ══════════════════════════════════════════════════════════════════════════════
#  DISCONNECT FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def disconnect_device(parent):
    """Disconnect from the currently connected device."""
    result = messagebox.askyesno(
        "Disconnect",
        "Are you sure you want to disconnect from the device?",
        parent=parent
    )
    if result:
        print("Device disconnected")
        messagebox.showinfo("Disconnect", "Device disconnected successfully.", parent=parent)
        return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone preview
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    root.title("VMS 3000 - Connection Test")
    root.geometry("400x300")
    root.configure(bg=T["win_bg"])

    fonts = {
        "ui_b": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
        "sm":   tkfont.Font(family="Segoe UI", size=9),
        "sm_b": tkfont.Font(family="Segoe UI", size=9,  weight="bold"),
        "mono": tkfont.Font(family="Consolas", size=10),
    }

    def on_direct_connect():
        dialog = DirectConnectDialog(root, fonts)
        dialog.show()

    def on_network_connect():
        dialog = NetworkConnectDialog(root, fonts)
        dialog.show()

    def on_disconnect():
        disconnect_device(root)

    # Test buttons
    btn_frame = tk.Frame(root, bg=T["win_bg"])
    btn_frame.pack(pady=50)

    tk.Button(
        btn_frame,
        text="Direct Connect",
        command=on_direct_connect,
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
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Network Connect",
        command=on_network_connect,
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
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Disconnect",
        command=on_disconnect,
        font=fonts["ui_b"],
        bg=T["led_amber"],
        fg="#1a1a00",
        activebackground="#d48800",
        activeforeground="#1a1a00",
        relief="flat",
        bd=0,
        padx=20,
        pady=10,
        cursor="hand2",
    ).pack(side="left", padx=5)

    root.mainloop()
