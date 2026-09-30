"""
Test script for VMS 3000 Toolbar with Connection functionality
"""

import tkinter as tk
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.toolbar import Toolbar


def main():
    root = tk.Tk()
    root.title("VMS 3000 - Toolbar Test")
    root.geometry("800x600")
    
    # Create toolbar
    toolbar = Toolbar(root, bg_color="#f4f6f9")
    
    # Set up callbacks
    toolbar.set_callback("new", lambda: print("New file created"))
    toolbar.set_callback("open", lambda: print("Open file dialog"))
    toolbar.set_callback("save", lambda: print("File saved"))
    toolbar.set_callback("print", lambda: print("Print document"))
    toolbar.set_callback("settings", lambda: print("Settings opened"))
    toolbar.set_callback("cut", lambda: print("Text cut"))
    toolbar.set_callback("copy", lambda: print("Text copied"))
    toolbar.set_callback("paste", lambda: print("Text pasted"))
    toolbar.set_callback("direct_connect", lambda result: print(f"Connected: {result}"))
    toolbar.set_callback("network_connect", lambda: print("Network connect initiated"))
    toolbar.set_callback("disconnect", lambda: print("Disconnected"))
    
    # Main content area
    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(fill="both", expand=True)
    
    # Add some content to demonstrate the toolbar
    content_label = tk.Label(
        main_frame,
        text="VMS 3000 Toolbar Demo\n\nClick the toolbar icons to test functionality:\n"
             "- File operations: New, Open, Save, Print, Settings\n"
             "- Clipboard: Cut, Copy, Paste\n"
             "- Connection: Click the 🔗 icon for connection options",
        bg="white",
        fg="black",
        font=("Arial", 12),
        justify="left"
    )
    content_label.pack(expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()
