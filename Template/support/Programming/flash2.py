#!/usr/bin/env python3
"""
Flash lev_single_image.hex to an ESP chip.

Usage:
    python flash.py COM3

Runs:
    esptool --port COM3 write_flash 0x0 lev_single_image.hex
"""

import importlib.util
import os
import subprocess
import sys

FIRMWARE = "lev_single_image.hex"
OFFSET = "0x0"


def main():
    # COM port is required, given as the only argument
    if len(sys.argv) != 2:
        sys.exit("Usage: python flash.py <COM_PORT>\nExample: python flash.py COM3")
    port = sys.argv[1]

    # Firmware file must be in the same folder as this script (or current folder)
    firmware = FIRMWARE
    if not os.path.isfile(firmware):
        firmware = os.path.join(os.path.dirname(os.path.abspath(__file__)), FIRMWARE)
    if not os.path.isfile(firmware):
        sys.exit(f"Error: {FIRMWARE} not found.")

    # Install esptool if missing
    if importlib.util.find_spec("esptool") is None:
        print("Installing esptool ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "esptool"])

    cmd = [sys.executable, "-m", "esptool", "--port", port, "write_flash", OFFSET, firmware]
    print("Running:", " ".join(cmd))
    code = subprocess.call(cmd)

    if code == 0:
        print("\nFlash complete. Press RESET on the board.")
    else:
        print("\nFlashing failed. Hold BOOT, tap RESET, release BOOT, then try again.")
    sys.exit(code)


if __name__ == "__main__":
    main()
