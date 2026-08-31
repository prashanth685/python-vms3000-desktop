"""
menubar.py — VMS 3000
Dark-navy menu bar with fixed-width items and crisp separators.
"""

import tkinter as tk
from theme import T


def build_menubar(root, fonts, commands: dict):
    """
    Attach a dark-navy OS menu bar to *root*.

    Expected command keys:
        new, open, save, save_as, connect, disconnect,
        calibrate, diag, comm, about
    """
    mb = tk.Menu(
        root,
        bg=T["menu_bg"],
        fg=T["menu_fg"],
        activebackground=T["menu_active_bg"],
        activeforeground=T["menu_active_fg"],
        font=fonts["menu"],
        relief="flat",
        bd=0,
    )
    root.config(menu=mb)

    # ── helper ──────────────────────────────────────────────────────
    def _drop(label, items):
        m = tk.Menu(
            mb,
            tearoff=0,
            bg=T["menu_drop_bg"],
            fg=T["menu_fg"],
            activebackground=T["menu_active_bg"],
            activeforeground=T["menu_active_fg"],
            selectcolor=T["menu_active_bg"],
            font=fonts["menu"],
            relief="flat",
            bd=1,
            postcommand=None,
        )
        for item in items:
            if item is None:
                m.add_separator()
            else:
                lbl, cmd, *rest = item
                state    = rest[0] if rest else tk.NORMAL
                accel    = rest[1] if len(rest) > 1 else ""
                m.add_command(
                    label=f"  {lbl}",
                    accelerator=accel,
                    command=cmd or (lambda: None),
                    state=state,
                )
        mb.add_cascade(label=f"  {label}  ", menu=m)

    # ── helper for submenu ───────────────────────────────────────────
    def _submenu(parent, label, items):
        m = tk.Menu(
            parent,
            tearoff=0,
            bg=T["menu_drop_bg"],
            fg=T["menu_fg"],
            activebackground=T["menu_active_bg"],
            activeforeground=T["menu_active_fg"],
            selectcolor=T["menu_active_bg"],
            font=fonts["menu"],
            relief="flat",
            bd=1,
        )
        for item in items:
            if item is None:
                m.add_separator()
            else:
                lbl, cmd, *rest = item
                state    = rest[0] if rest else tk.NORMAL
                accel    = rest[1] if len(rest) > 1 else ""
                m.add_command(
                    label=f"  {lbl}",
                    accelerator=accel,
                    command=cmd or (lambda: None),
                    state=state,
                )
        parent.add_cascade(label=f"  {label}  ", menu=m)

    # ── File ────────────────────────────────────────────────────────
    file_menu = tk.Menu(
        mb,
        tearoff=0,
        bg=T["menu_drop_bg"],
        fg=T["menu_fg"],
        activebackground=T["menu_active_bg"],
        activeforeground=T["menu_active_fg"],
        selectcolor=T["menu_active_bg"],
        font=fonts["menu"],
        relief="flat",
        bd=1,
    )
    
    file_menu.add_command(label="  New",            accelerator="Ctrl+N", command=commands.get("new") or (lambda: None))
    file_menu.add_command(label="  Open…",          accelerator="Ctrl+O", command=commands.get("open") or (lambda: None))
    file_menu.add_command(label="  Save",           accelerator="Ctrl+S", command=commands.get("save") or (lambda: None))
    file_menu.add_command(label="  Save As…",       accelerator="Ctrl+Shift+S", command=commands.get("save_as") or (lambda: None))
    
    # Connection submenu
    connection_menu = tk.Menu(
        file_menu,
        tearoff=0,
        bg=T["menu_drop_bg"],
        fg=T["menu_fg"],
        activebackground=T["menu_active_bg"],
        activeforeground=T["menu_active_fg"],
        selectcolor=T["menu_active_bg"],
        font=fonts["menu"],
        relief="flat",
        bd=1,
    )
    connection_menu.add_command(label="  Direct Connect",   command=commands.get("direct_connect") or (lambda: None))
    connection_menu.add_command(label="  Network Connect",  command=commands.get("network_connect") or (lambda: None))
    connection_menu.add_command(label="  Disconnect",       command=commands.get("disconnect") or (lambda: None))
    file_menu.add_cascade(label="  Connection  ", menu=connection_menu)
    
    file_menu.add_separator()
    file_menu.add_command(label="  Print…",         accelerator="Ctrl+P", command=None)
    file_menu.add_separator()
    file_menu.add_command(label="  Exit",           accelerator="Alt+F4", command=root.destroy)
    
    mb.add_cascade(label="  File  ", menu=file_menu)

    # ── Edit ────────────────────────────────────────────────────────
    _drop("Edit", [
        ("Undo",           None,  tk.DISABLED, "Ctrl+Z"),
        ("Redo",           None,  tk.DISABLED, "Ctrl+Y"),
        None,
        ("Cut",            None,  tk.NORMAL,  "Ctrl+X"),
        ("Copy",           None,  tk.NORMAL,  "Ctrl+C"),
        ("Paste",          None,  tk.NORMAL,  "Ctrl+V"),
        None,
        ("Select All",     None,  tk.NORMAL,  "Ctrl+A"),
    ])

    # ── Utilities ───────────────────────────────────────────────────
    _drop("Utilities", [
        ("Connect",            commands.get("connect"),     tk.NORMAL),
        ("Disconnect",         commands.get("disconnect"),  tk.NORMAL),
        None,
        ("Calibrate…",         commands.get("calibrate"),  tk.NORMAL),
        ("Diagnostics…",       commands.get("diag"),       tk.NORMAL),
        ("Firmware Update…",   None,                       tk.NORMAL),
    ])

    # ── Options ─────────────────────────────────────────────────────
    _drop("Options", [
        ("Preferences…",             None,                    tk.NORMAL),
        ("Communication Settings…",  commands.get("comm"),    tk.NORMAL),
        ("Rack Address…",            None,                    tk.NORMAL),
        None,
        ("Theme",                    None,                    tk.DISABLED),
    ])

    # ── View ────────────────────────────────────────────────────────
    _drop("View", [
        ("Zoom In",      None, tk.NORMAL, "Ctrl++"),
        ("Zoom Out",     None, tk.NORMAL, "Ctrl+-"),
        ("Reset Zoom",   None, tk.NORMAL, "Ctrl+0"),
        None,
        ("Full Screen",  None, tk.NORMAL, "F11"),
        ("Reset Layout", None, tk.NORMAL),
    ])

    # ── Help ────────────────────────────────────────────────────────
    _drop("Help", [
        ("Help Topics",      None,                    tk.NORMAL, "F1"),
        ("Quick Start Guide",None,                    tk.NORMAL),
        None,
        ("Check for Updates",None,                    tk.NORMAL),
        ("About VMS 3000",   commands.get("about"),  tk.NORMAL),
    ])