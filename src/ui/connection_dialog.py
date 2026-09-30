"""
connection_dialog.py — VMS 3000 Direct Connection Dialog
Dialog for direct connect with Rack Address, COM Port, and Baud Rate
"""

import tkinter as tk
from tkinter import ttk


class ConnectionDialog:
    """Direct Connect dialog as shown in the reference image."""
    
    def __init__(self, parent, available_com_ports=None, bg_color="#f4f6f9"):
        self.parent = parent
        self.available_com_ports = available_com_ports or []
        self.bg_color = bg_color
        self.dialog = None
        self.result = None
        
        # Default values
        self.rack_address = tk.StringVar(value="1")
        self.com_port = tk.StringVar(value=available_com_ports[0] if available_com_ports else "COM1")
        self.baud_rate = tk.StringVar(value="115200")
        self.password = tk.StringVar(value="")
    
    def show(self):
        """Show the connection dialog and return the result."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Direct Connect")
        self.dialog.configure(bg=self.bg_color)
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self._build_ui()
        
        # Set minimum size to ensure all content is visible
        self.dialog.update_idletasks()
        width = max(400, self.dialog.winfo_reqwidth())
        height = max(350, self.dialog.winfo_reqheight())
        self.dialog.geometry(f"{width}x{height}")
        
        # Center dialog after setting size
        self._center_dialog()
        
        self.parent.wait_window(self.dialog)
        return self.result
    
    def _center_dialog(self):
        """Center dialog on screen."""
        self.dialog.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Get dialog dimensions
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate center position
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _build_ui(self):
        """Build the dialog UI matching the reference image."""
        main_frame = tk.Frame(self.dialog, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # ── Connect Password ───────────────────────────────────────────────────
        password_frame = tk.Frame(main_frame, bg=self.bg_color)
        password_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            password_frame,
            text="Connect Password:",
            bg=self.bg_color,
            fg="black",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        password_entry = tk.Entry(
            password_frame,
            textvariable=self.password,
            show="*",
            font=("Arial", 10),
            relief="solid",
            borderwidth=1
        )
        password_entry.pack(fill="x", pady=(5, 0))
        
        # ── Rack Address ───────────────────────────────────────────────────────
        rack_frame = tk.Frame(main_frame, bg=self.bg_color)
        rack_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            rack_frame,
            text="Rack Address:",
            bg=self.bg_color,
            fg="black",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        rack_combo = ttk.Combobox(
            rack_frame,
            textvariable=self.rack_address,
            values=[str(i) for i in range(1, 256)],  # 1-255
            state="readonly",
            font=("Arial", 10)
        )
        rack_combo.pack(fill="x", pady=(5, 0))
        
        # ── COM Port ───────────────────────────────────────────────────────────
        com_frame = tk.Frame(main_frame, bg=self.bg_color)
        com_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            com_frame,
            text="COM Port:",
            bg=self.bg_color,
            fg="black",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        com_combo = ttk.Combobox(
            com_frame,
            textvariable=self.com_port,
            values=self.available_com_ports if self.available_com_ports else ["COM1"],
            state="readonly",
            font=("Arial", 10)
        )
        com_combo.pack(fill="x", pady=(5, 0))
        
        # ── Baud Rate ─────────────────────────────────────────────────────────
        baud_frame = tk.Frame(main_frame, bg=self.bg_color)
        baud_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(
            baud_frame,
            text="Baud Rate:",
            bg=self.bg_color,
            fg="black",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        baud_combo = ttk.Combobox(
            baud_frame,
            textvariable=self.baud_rate,
            values=["9600", "19200", "57600", "115200"],  # Fixed typo from 119200 to 19200
            state="readonly",
            font=("Arial", 10)
        )
        baud_combo.pack(fill="x", pady=(5, 0))
        
        # ── Buttons ───────────────────────────────────────────────────────────
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill="x", pady=(15, 0))
        
        # Connect button
        connect_btn = tk.Button(
            button_frame,
            text="Connect",
            command=self._on_connect,
            bg="#4a90e2",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        connect_btn.pack(side="left", padx=(0, 8))
        
        # Browse button
        browse_btn = tk.Button(
            button_frame,
            text="Browse",
            command=self._on_browse,
            bg="#e0e0e0",
            fg="black",
            font=("Arial", 10),
            relief="raised",
            bd=2,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        browse_btn.pack(side="left", padx=(0, 8))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            bg="#e0e0e0",
            fg="black",
            font=("Arial", 10),
            relief="raised",
            bd=2,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        cancel_btn.pack(side="left", padx=(0, 8))
        
        # Help button
        help_btn = tk.Button(
            button_frame,
            text="Help",
            command=self._on_help,
            bg="#e0e0e0",
            fg="black",
            font=("Arial", 10),
            relief="raised",
            bd=2,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        help_btn.pack(side="right")
    
    def _on_connect(self):
        """Handle Connect button click."""
        self.result = {
            "password": self.password.get(),
            "rack_address": self.rack_address.get(),
            "com_port": self.com_port.get(),
            "baud_rate": self.baud_rate.get()
        }
        self.dialog.destroy()
    
    def _on_browse(self):
        """Handle Browse button click."""
        print("Browse clicked")
        # TODO: Implement browse functionality
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def _on_help(self):
        """Handle Help button click."""
        print("Help clicked")
        # TODO: Implement help functionality
