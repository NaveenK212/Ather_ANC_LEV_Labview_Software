#!/usr/bin/env python3
"""
Flash a .hex file to an ESP chip and show esptool's live progress.

Usage:
    python flash.py <COM_PORT> <HEX_FILE>

Example:
    python flash.py COM3 lev_single_image.hex

Runs:
    esptool --port COM3 write_flash 0x0 lev_single_image.hex
"""

import importlib.util
import os
import subprocess
import sys

OFFSET = "0x0"


def get_python():
    """IDLE uses pythonw.exe (no console, output lost). Prefer python.exe."""
    exe = sys.executable
    if exe.lower().endswith("pythonw.exe"):
        candidate = exe[:-len("pythonw.exe")] + "python.exe"
        if os.path.isfile(candidate):
            return candidate
    return exe


def run(cmd):
    """Run a command and stream its output live, including the progress percentage."""
    print("Running:", " ".join(cmd), "\n")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
        errors="replace",
    )
    while True:
        ch = proc.stdout.read(1)
        if ch == "" and proc.poll() is not None:
            break
        if ch:
            sys.stdout.write(ch)
            sys.stdout.flush()
    return proc.wait()


def main():
    # Both COM port and .hex file are required arguments
    if len(sys.argv) != 3:
        sys.exit("Usage: python flash.py <COM_PORT> <HEX_FILE>\n"
                 "Example: python flash.py COM3 lev_single_image.hex")
    port = sys.argv[1]
    firmware = sys.argv[2]

    # Find the firmware file (given path, or next to this script)
    if not os.path.isfile(firmware):
        alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), firmware)
        if os.path.isfile(alt):
            firmware = alt
        else:
            sys.exit(f"Error: file not found: {firmware}")
    firmware = os.path.abspath(firmware)

    python = get_python()

    # Install esptool if missing
    if importlib.util.find_spec("esptool") is None:
        print("Installing esptool ...")
        if run([python, "-m", "pip", "install", "esptool"]) != 0:
            sys.exit("Could not install esptool.")

    code = run([python, "-m", "esptool", "--port", port, "write_flash", OFFSET, firmware])

    if code == 0:
        print("\nFlash complete. Press RESET on the board.")
    else:
        print("\nFlashing failed. Hold BOOT, tap RESET, release BOOT, then try again.")
    sys.exit(code)


if __name__ == "__main__":
    main()
