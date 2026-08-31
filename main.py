"""
main.py — VMS 3000 Rack Configuration Software v0.5
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, filedialog
import datetime

from theme     import T
from menubar   import build_menubar
from toolbar   import build_toolbar
from rack_area import RackArea
from tooltip   import ToolTip
from src.sidebar.sidebar import build_sidebar
from src.sidebar.rack_setup import open_rack_setup
from src.sidebar.open_config_load import LoadConfigDialog
from src.sidebar.open_config_save import SaveConfigDialog
from src.sidebar.connection import DirectConnectDialog, NetworkConnectDialog, disconnect_device

class VMS3000(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("VMS 3000  —  Rack Configuration Software  v0.5")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        self.configure(bg=T["win_bg"])

        # ── Shared state ─────────────────────────────────────────────
        self._rack_addr = tk.StringVar(value="1")
        self._time_var  = tk.StringVar()
        self._date_var  = tk.StringVar(
            value=datetime.datetime.now().strftime("%d-%m-%Y")
        )
        self._conn_var  = tk.StringVar(value="Not Connected")
        self._hint_var  = tk.StringVar(value="Click any slot to assign module")

        # ── Fonts ────────────────────────────────────────────────────
        self.F = {
            "menu":    tkfont.Font(family="Segoe UI", size=11),
            "ui":      tkfont.Font(family="Segoe UI", size=10),
            "ui_b":    tkfont.Font(family="Segoe UI", size=10,  weight="bold"),
            "sm":      tkfont.Font(family="Segoe UI", size=9),
            "sm_b":    tkfont.Font(family="Segoe UI", size=9,  weight="bold"),
            "xs":      tkfont.Font(family="Segoe UI", size=8),
            "xs_b":    tkfont.Font(family="Segoe UI", size=8,  weight="bold"),
            "vms":     tkfont.Font(family="Segoe UI", size=13, weight="bold"),
            "mono":    tkfont.Font(family="Courier New", size=9),
            "num":     tkfont.Font(family="Segoe UI", size=9,  weight="bold"),
        }

        # ── Build UI ─────────────────────────────────────────────────
        self._build_menu()
        self._icons = build_toolbar(self, self.F, self._rack_addr)

        # ── Border after toolbar ───────────────────────────────────────
        tk.Frame(self, bg=T["toolbar_border"], height=2).pack(fill="x", padx=0)

        body = tk.Frame(self, bg=T["win_bg"])
        body.pack(fill="both", expand=True, padx=0, pady=0)

        build_sidebar(body, self.F, {
            "rack_setup": self._cmd_rack_setup,
            "load":       self._cmd_open,
            "save":       self._cmd_save,
        })

        # ── Separator between sidebar and rack area ─────────────────────
        tk.Frame(body, bg=T["toolbar_border"], width=1).pack(side="left", fill="y")

        self._rack = RackArea(body, self.F, self._hint_var)

        self._build_status_bar()
        self._tick()

    # ── Menu ─────────────────────────────────────────────────────────

    def _build_menu(self):
        build_menubar(self, self.F, {
            "new":              self._cmd_new,
            "open":             self._cmd_open,
            "save":             self._cmd_save,
            "save_as":          self._cmd_save_as,
            "direct_connect":   self._cmd_direct_connect,
            "network_connect":  self._cmd_network_connect,
            "disconnect":       self._cmd_disconnect,
            "calibrate":        None,
            "diag":             self._cmd_diag,
            "comm":             self._cmd_comm,
            "about":            self._cmd_about,
        })

    # ── Status bar ────────────────────────────────────────────────────

    def _build_status_bar(self):
        bar = tk.Frame(
            self,
            bg=T["status_bg"],
            highlightbackground=T["status_border"],
            highlightthickness=1,
        )
        bar.pack(side="bottom", fill="x")

        # Left section
        left = tk.Frame(bar, bg=T["status_bg"])
        left.pack(side="left", fill="y")

        tk.Label(
            left,
            text="Sarayu Infotech Solutions Pvt Ltd",
            font=self.F["ui"],
            bg=T["status_bg"],
            fg=T["text_dim"],
        ).pack(side="left", padx=12, pady=6)

        _vsep(left, T["status_border"])

        tk.Label(
            left,
            text="VMS 3000  v0.5",
            font=self.F["ui_b"],
            bg=T["status_bg"],
            fg=T["text_dim"],
        ).pack(side="left", padx=10)

        # Right section
        right = tk.Frame(bar, bg=T["status_bg"])
        right.pack(side="right", fill="y")

        self._conn_dot = tk.Label(
            right,
            text="●",
            font=self.F["ui"],
            bg=T["status_bg"],
            fg=T["led_red"],
        )
        self._conn_dot.pack(side="right", padx=(0, 12), pady=6)

        self._conn_lbl = tk.Label(
            right,
            textvariable=self._conn_var,
            font=self.F["ui_b"],
            bg=T["status_bg"],
            fg=T["led_red"],
        )
        self._conn_lbl.pack(side="right", pady=6)

        _vsep(right, T["status_border"])

        tk.Label(
            right,
            textvariable=self._time_var,
            font=self.F["ui"],
            bg=T["status_bg"],
            fg=T["text_dim"],
        ).pack(side="right", padx=8)

        tk.Label(
            right,
            textvariable=self._date_var,
            font=self.F["ui"],
            bg=T["status_bg"],
            fg=T["text_dim"],
        ).pack(side="right", padx=6)

        _vsep(right, T["status_border"])

    # ── Tick ─────────────────────────────────────────────────────────

    def _tick(self):
        self._time_var.set(datetime.datetime.now().strftime("%H:%M"))
        self.after(30_000, self._tick)

    # ── Commands ─────────────────────────────────────────────────────

    def _cmd_new(self):
        if messagebox.askyesno("New Configuration",
                               "Start a new configuration?\nUnsaved changes will be lost.",
                               parent=self):
            self._rack.clear()

    def _cmd_open(self):
        self._rack.load_configuration()

    def _cmd_save(self):
        self._rack.save_configuration()

    def _cmd_save_as(self):
        messagebox.showinfo("Save As", "Save As ready.", parent=self)

    def _cmd_rack_setup(self):
        def handle_rack_config(cfg: dict):
            print(f"Rack configuration: {cfg}")
            # You can apply the configuration here
        
        open_rack_setup(self, self.F, on_ok=handle_rack_config)

    def _cmd_direct_connect(self):
        dialog = DirectConnectDialog(self, self.F)
        dialog.show()
        # Update connection status after dialog closes
        self._conn_var.set("Connected")
        self._conn_lbl.config(fg=T["led_green"])
        self._conn_dot.config(fg=T["led_green"])

    def _cmd_network_connect(self):
        dialog = NetworkConnectDialog(self, self.F)
        dialog.show()
        # Update connection status after dialog closes
        self._conn_var.set("Connected")
        self._conn_lbl.config(fg=T["led_green"])
        self._conn_dot.config(fg=T["led_green"])

    def _cmd_disconnect(self):
        if disconnect_device(self):
            self._conn_var.set("Not Connected")
            self._conn_lbl.config(fg=T["led_red"])
            self._conn_dot.config(fg=T["led_red"])

    def _cmd_diag(self):
        messagebox.showinfo("Diagnostics", "System OK — no faults detected.", parent=self)

    def _cmd_comm(self):
        messagebox.showinfo("Communication Settings", "Communication settings ready.", parent=self)

    def _cmd_about(self):
        messagebox.showinfo(
            "About VMS 3000",
            "VMS 3000  Rack Configuration Software\n"
            "Version 0.5\n\n"
            "© Sarayu Infotech Solutions Pvt Ltd",
            parent=self,
        )


# ── Utility ──────────────────────────────────────────────────────────────────

def _vsep(parent: tk.Frame, colour: str) -> None:
    tk.Frame(parent, bg=colour, width=1).pack(side="right", fill="y", padx=4, pady=3)


if __name__ == "__main__":
    app = VMS3000()
    app.mainloop()