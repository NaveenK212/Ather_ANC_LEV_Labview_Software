#!/usr/bin/env python3
"""
Flash a .hex firmware file to an ESP chip using:

    esptool write_flash 0x0 filename.hex

Usage:
    python flash.py COM3                  # flash lev_single_image.hex at 0x0 on COM3
    python flash.py                       # use DEFAULT_PORT below, or auto-detect
    python flash.py COM3 -f other.hex -o 0x0
    python flash.py COM3 --erase          # erase flash first
    python flash.py COM3 --baud 115200
"""

import argparse
import importlib.util
import os
import subprocess
import sys

DEFAULT_FIRMWARE = "lev_single_image.hex"
DEFAULT_OFFSET = "0x0"
DEFAULT_BAUD = "921600"
DEFAULT_PORT = None  # e.g. "COM3". Set this if you run from IDLE (no command-line args)


def get_python():
    """IDLE runs scripts with pythonw.exe (no console, output lost). Prefer python.exe."""
    exe = sys.executable
    if exe.lower().endswith("pythonw.exe"):
        candidate = exe[:-len("pythonw.exe")] + "python.exe"
        if os.path.isfile(candidate):
            return candidate
    return exe


PYTHON = get_python()


def run(cmd):
    """Run a command and stream its output live (works in IDLE and in a terminal)."""
    print("\n>", " ".join(cmd))
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


def ensure_esptool():
    """pip install esptool if it is not installed."""
    if importlib.util.find_spec("esptool") is None:
        print("esptool not found. Installing ...")
        if run([PYTHON, "-m", "pip", "install", "esptool"]) != 0:
            sys.exit("Could not install esptool. Try:  pip install esptool")


def find_port():
    """Return the first likely ESP serial port, or None to let esptool auto-detect."""
    from serial.tools import list_ports

    ports = list(list_ports.comports())
    if not ports:
        return None
    keywords = ("cp210", "ch340", "ch910", "ftdi", "usb serial", "usb-serial",
                "usb jtag", "uart", "esp")
    for p in ports:
        desc = f"{p.description} {p.manufacturer or ''}".lower()
        if any(k in desc for k in keywords):
            return p.device
    return ports[0].device


def main():
    parser = argparse.ArgumentParser(description="Flash a .hex file to an ESP chip")
    parser.add_argument("port_pos", nargs="?", default=None, metavar="PORT",
                        help="serial port, e.g. COM3 or /dev/ttyUSB0")
    parser.add_argument("-p", "--port", default=None, help="serial port (same as PORT)")
    parser.add_argument("-f", "--file", default=DEFAULT_FIRMWARE, help="firmware .hex file")
    parser.add_argument("-o", "--offset", default=DEFAULT_OFFSET, help="flash offset (default 0x0)")
    parser.add_argument("-b", "--baud", default=DEFAULT_BAUD, help="baud rate")
    parser.add_argument("--erase", action="store_true", help="erase the entire flash first")
    args = parser.parse_args()

    # Find the firmware file (current folder first, then next to this script)
    firmware = args.file
    if not os.path.isfile(firmware):
        alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), firmware)
        if os.path.isfile(alt):
            firmware = alt
        else:
            sys.exit(f"Error: firmware file not found: {args.file}")
    firmware = os.path.abspath(firmware)

    ensure_esptool()

    port = args.port or args.port_pos or DEFAULT_PORT or find_port()
    if port:
        print(f"Using port: {port}")
    else:
        print("No serial port found; letting esptool try to auto-detect.")

    base = [PYTHON, "-m", "esptool", "--baud", str(args.baud)]
    if port:
        base += ["--port", port]

    if args.erase:
        if run(base + ["erase_flash"]) != 0:
            sys.exit("Erase failed.")

    # Equivalent to:  esptool write_flash 0x0 filename.hex
    code = run(base + ["write_flash", args.offset, firmware])

    if code != 0:
        print("\nFlashing failed. Things to try:")
        print("  - Hold BOOT, tap RESET, release BOOT, then run again")
        print("  - Close any program using the port (serial monitor, Arduino IDE, PuTTY)")
        print("  - Use a data-capable USB cable")
        print("  - Update esptool so it reads .hex files:  pip install --upgrade esptool")
        print("  - Try a lower baud rate:  python flash.py COM3 --baud 115200")
        sys.exit(code)

    print("\nFlash complete. Press RESET on the board to run the new firmware.")


if __name__ == "__main__":
    main()
