"""
Test script for Relay Configuration Dialog with channel configuration slots
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from points.relay_config import RelayConfigDialog

def main():
    root = tk.Tk()
    root.title("Test Relay Configuration Dialog")
    root.geometry("400x300")

    # Simulate rack configuration with some modules
    rack_config = {
        "0_1": "No Modules",
        "0_2": "No Modules", 
        "0_3": "No Modules",
        "0_4": "No Modules",
        "0_5": "VMM-6M",  # VMM module in slot 5
        "0_6": "No Modules",
        "0_7": "3000/12M/DIS",  # DIS module in slot 7
        "0_8": "No Modules",
        "0_9": "No Modules",
        "0_10": "No Modules",
        "0_11": "No Modules",
    }

    def open_relay_dialog():
        dlg = RelayConfigDialog(
            root, 
            slot_num=5,  # Relay slot number
            rack_type="VMM/12T/DISP",
            config_id="CONFIG-001",
            selected_slot=5,  # Initially select slot 5 (which has VMM-6M)
            rack_config=rack_config
        )
        dlg.show()

    btn = tk.Button(root, text="Open Relay Configuration Dialog", command=open_relay_dialog)
    btn.pack(pady=50)

    info_label = tk.Label(root, text="This will show channel configuration slots\nfor the selected module (e.g., VMM-6M in slot 5)")
    info_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
