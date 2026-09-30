"""
com_port_detector.py — VMS 3000 COM Port Detection
Detects available COM ports on the system
"""

import sys
import platform


def get_available_com_ports():
    """Get list of available COM ports on the system.
    
    Returns:
        list: List of COM port names (e.g., ["COM1", "COM3", "COM4"])
    """
    system = platform.system()
    
    if system == "Windows":
        return _get_windows_com_ports()
    elif system == "Linux":
        return _get_linux_serial_ports()
    elif system == "Darwin":  # macOS
        return _get_macos_serial_ports()
    else:
        # Fallback for unknown systems
        return ["COM1", "COM2", "COM3"]


def _get_windows_com_ports():
    """Get COM ports on Windows using pyserial or fallback."""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    except ImportError:
        # Fallback if pyserial is not installed
        return _get_windows_com_ports_fallback()
    except Exception as e:
        print(f"Pyserial detection failed: {e}")
        return _get_windows_com_ports_fallback()


def _get_windows_com_ports_fallback():
    """Fallback method for Windows COM port detection - simple defaults."""
    # Return common COM ports as fallback
    return ["COM1", "COM2", "COM3", "COM4"]


def _get_linux_serial_ports():
    """Get serial ports on Linux."""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    except ImportError:
        # Fallback for Linux without pyserial
        import os
        com_ports = []
        try:
            # Check /dev for serial devices
            dev_files = os.listdir("/dev")
            for file in dev_files:
                if file.startswith("ttyS") or file.startswith("ttyUSB") or file.startswith("ttyACM"):
                    com_ports.append(f"/dev/{file}")
        except (OSError, PermissionError):
            pass
        
        return com_ports if com_ports else ["/dev/ttyS0", "/dev/ttyS1"]
    except Exception:
        return ["/dev/ttyS0", "/dev/ttyS1"]


def _get_macos_serial_ports():
    """Get serial ports on macOS."""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    except ImportError:
        # Fallback for macOS without pyserial
        import os
        com_ports = []
        try:
            # Check /dev for serial devices
            dev_files = os.listdir("/dev")
            for file in dev_files:
                if file.startswith("tty."):
                    com_ports.append(f"/dev/{file}")
        except (OSError, PermissionError):
            pass
        
        return com_ports if com_ports else ["/dev/tty.usbserial", "/dev/tty.usbmodem"]
    except Exception:
        return ["/dev/tty.usbserial", "/dev/tty.usbmodem"]


def test_com_port_detection():
    """Test function to verify COM port detection."""
    ports = get_available_com_ports()
    print(f"Detected COM ports: {ports}")
    return ports


if __name__ == "__main__":
    test_com_port_detection()
