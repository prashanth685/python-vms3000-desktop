"""
toolbar.py — VMS 3000 Interactive Toolbar
Provides toolbar icons with connection functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from icons import IconPainter
from src.ui.connection_dialog import ConnectionDialog
from src.ui.com_port_detector import get_available_com_ports


class Toolbar:
    """Interactive toolbar with file operations and connection management."""
    
    def __init__(self, parent, bg_color="#f4f6f9"):
        self.parent = parent
        self.bg_color = bg_color
        self.icon_painter = IconPainter(bg_hex=bg_color)
        self._callbacks = {}
        
        # Create toolbar frame
        self.frame = tk.Frame(parent, bg=bg_color, height=40, relief="raised", bd=1)
        self.frame.pack(side="top", fill="x")
        self.frame.pack_propagate(False)
        
        # Build toolbar buttons
        self._build_toolbar()
    
    def _build_toolbar(self):
        """Build toolbar buttons with icons."""
        button_configs = [
            ("new", "New", self._on_new),
            ("open", "Open", self._on_open),
            ("save", "Save", self._on_save),
            ("print", "Print", self._on_print),
            ("settings", "Settings", self._on_settings),
            ("cut", "Cut", self._on_cut),
            ("copy", "Copy", self._on_copy),
            ("paste", "Paste", self._on_paste),
        ]
        
        for icon_name, tooltip, callback in button_configs:
            self._create_toolbar_button(icon_name, tooltip, callback)
        
        # Add separator
        separator = tk.Frame(self.frame, bg=self.bg_color, width=2, height=30)
        separator.pack(side="left", padx=8)
        
        # Add connection button with dropdown
        self._create_connection_button()
    
    def _create_toolbar_button(self, icon_name, tooltip, callback):
        """Create a single toolbar button."""
        try:
            icon = self.icon_painter.get(icon_name)
        except Exception:
            # Fallback if icon fails to load
            icon = None
        
        btn = tk.Button(
            self.frame,
            image=icon if icon else None,
            text=icon_name[0].upper() if not icon else "",
            command=callback,
            bg=self.bg_color,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            activebackground="#e2e8f0"
        )
        btn.pack(side="left", padx=2)
        
        # Add tooltip
        self._add_tooltip(btn, tooltip)
        
        return btn
    
    def _create_connection_button(self):
        """Create connection button with dropdown menu."""
        try:
            icon = self.icon_painter.get("connection")
        except Exception:
            icon = None
        
        self.connection_btn = tk.Button(
            self.frame,
            image=icon if icon else None,
            text="🔗" if not icon else "",
            command=self._show_connection_menu,
            bg=self.bg_color,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            activebackground="#e2e8f0"
        )
        self.connection_btn.pack(side="left", padx=2)
        self._add_tooltip(self.connection_btn, "Connection")
    
    def _show_connection_menu(self):
        """Show connection dropdown menu."""
        menu = tk.Menu(self.parent, tearoff=0)
        menu.add_command(label="Direct connect", command=self._on_direct_connect)
        menu.add_command(label="Network connect", command=self._on_network_connect)
        menu.add_separator()
        menu.add_command(label="Disconnect", command=self._on_disconnect)
        
        # Position menu below the button
        try:
            x = self.connection_btn.winfo_rootx()
            y = self.connection_btn.winfo_rooty() + self.connection_btn.winfo_height()
        except Exception:
            # Fallback if window isn't mapped yet
            x = self.parent.winfo_rootx() + 100
            y = self.parent.winfo_rooty() + 50
        
        menu.post(x, y)
    
    def _add_tooltip(self, widget, text):
        """Add tooltip to widget."""
        def on_enter(event):
            tooltip = tk.Toplevel(self.parent)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                bg="#ffffe0",
                fg="black",
                relief="solid",
                borderwidth=1,
                font=("Arial", 8)
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    # ── Callback methods ──────────────────────────────────────────────────────
    def _on_new(self):
        if "new" in self._callbacks:
            self._callbacks["new"]()
        else:
            print("New clicked")
    
    def _on_open(self):
        if "open" in self._callbacks:
            self._callbacks["open"]()
        else:
            print("Open clicked")
    
    def _on_save(self):
        if "save" in self._callbacks:
            self._callbacks["save"]()
        else:
            print("Save clicked")
    
    def _on_print(self):
        if "print" in self._callbacks:
            self._callbacks["print"]()
        else:
            print("Print clicked")
    
    def _on_settings(self):
        if "settings" in self._callbacks:
            self._callbacks["settings"]()
        else:
            print("Settings clicked")
    
    def _on_cut(self):
        if "cut" in self._callbacks:
            self._callbacks["cut"]()
        else:
            print("Cut clicked")
    
    def _on_copy(self):
        if "copy" in self._callbacks:
            self._callbacks["copy"]()
        else:
            print("Copy clicked")
    
    def _on_paste(self):
        if "paste" in self._callbacks:
            self._callbacks["paste"]()
        else:
            print("Paste clicked")
    
    def _on_direct_connect(self):
        """Open direct connection dialog."""
        com_ports = get_available_com_ports()
        dialog = ConnectionDialog(self.parent, com_ports)
        result = dialog.show()
        if result:
            print(f"Direct connect: {result}")
            if "direct_connect" in self._callbacks:
                self._callbacks["direct_connect"](result)
    
    def _on_network_connect(self):
        if "network_connect" in self._callbacks:
            self._callbacks["network_connect"]()
        else:
            print("Network connect clicked")
    
    def _on_disconnect(self):
        if "disconnect" in self._callbacks:
            self._callbacks["disconnect"]()
        else:
            print("Disconnect clicked")
    
    # ── Public API for callbacks ───────────────────────────────────────────────
    def set_callback(self, action, callback):
        """Set callback for toolbar action."""
        self._callbacks[action] = callback
