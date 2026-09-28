"""
Test script for Proximity Monitor 3000 Configuration Dialog
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from points.proximiter12m_ridial import ProximityMonitor3000ConfigDialog

def main():
    root = tk.Tk()
    root.title("Test Proximity Monitor 3000 Dialog")
    root.geometry("300x200")

    def open_12m_dialog():
        dlg = ProximityMonitor3000ConfigDialog(root, slot_num=1, model="12M/DIS")
        dlg.show()

    def open_6m_dialog():
        dlg = ProximityMonitor3000ConfigDialog(root, slot_num=1, model="6M")
        dlg.show()

    btn_12m = tk.Button(root, text="Open 12M/DIS Dialog", command=open_12m_dialog)
    btn_12m.pack(pady=20)

    btn_6m = tk.Button(root, text="Open 6M Dialog", command=open_6m_dialog)
    btn_6m.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
