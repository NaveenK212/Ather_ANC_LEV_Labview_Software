import csv
import struct
import time
from datetime import datetime

from pymodbus.client import ModbusSerialClient

# ----------------------------- Settings ------------------------------------
PORT = "COM7"
BAUDRATE = 9600
SLAVE_ID = 1
POLL_SECONDS = 1.0

# Frequency register. Leave as None to auto-detect on start-up, or put the
# address from the manual / a previous scan here (e.g. FREQ_ADDRESS = 85).
FREQ_ADDRESS = None
FREQ_FUNCTION = "holding"        # "holding" or "input"
SCAN_RANGE = (0, 400)            # addresses tried by the auto-detect

LOG_CSV = True
CSV_FILE = "elite300_log.csv"

# Phase 1 measurements (0-based addresses, 2 registers each)
REGISTERS = {
    "Voltage (V)": 99,
    "Current (A)": 113,
    "Power Factor": 133,
    "Active Power (W)": 141,
    "Reactive Power (var)": 149,
    "Apparent Power (VA)": 157,
}
# ---------------------------------------------------------------------------

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=2,
)


def _read(func, address, count):
    fn = client.read_holding_registers if func == "holding" else client.read_input_registers
    try:
        return fn(address=address, count=count, device_id=SLAVE_ID)  # pymodbus 3.10+
    except TypeError:
        return fn(address=address, count=count, slave=SLAVE_ID)      # older pymodbus 3.x


def read_float(address, func="holding"):
    """Read a 32-bit float stored in 2 registers (word-swapped)."""
    result = _read(func, address, 2)
    if result.isError():
        raise IOError(str(result))
    hi, lo = result.registers[1], result.registers[0]
    return struct.unpack(">f", struct.pack(">HH", hi, lo))[0]


def find_frequency():
    """Scan for a float that looks like mains frequency (about 50 or 60 Hz)."""
    print("Scanning for the frequency register (this can take a minute)...")
    for func in ("holding", "input"):
        for addr in range(*SCAN_RANGE):
            try:
                v = read_float(addr, func)
            except Exception:
                continue
            if not (45.0 <= v <= 65.0):
                continue

            # Re-read a few times to make sure it is stable and plausible
            try:
                samples = [v]
                for _ in range(3):
                    time.sleep(0.4)
                    samples.append(read_float(addr, func))
            except Exception:
                continue

            mean = sum(samples) / len(samples)
            spread = max(samples) - min(samples)
            near_50 = 49.0 <= mean <= 51.0
            near_60 = 59.0 <= mean <= 61.0
            if spread < 0.5 and (near_50 or near_60):
                print(f"Frequency found: {func} register {addr} = {mean:.3f} Hz")
                return func, addr
    print("Frequency register not found. Set FREQ_ADDRESS manually.")
    return None


def main():
    if not client.connect():
        print("Unable to connect")
        return

    print("Connected to ELITE 300\n")

    # Build the list of items to read: (name, address, function)
    items = [(name, addr, "holding") for name, addr in REGISTERS.items()]

    if FREQ_ADDRESS is not None:
        items.insert(1, ("Frequency (Hz)", FREQ_ADDRESS, FREQ_FUNCTION))
    else:
        found = find_frequency()
        if found:
            items.insert(1, ("Frequency (Hz)", found[1], found[0]))

    names = [n for n, _, _ in items]

    csv_file = None
    writer = None
    if LOG_CSV:
        csv_file = open(CSV_FILE, "a", newline="")
        writer = csv.writer(csv_file)
        if csv_file.tell() == 0:
            writer.writerow(["Timestamp"] + names)

    print("\nReading Phase 1 measurements. Press Ctrl+C to stop.\n")

    try:
        while True:
            values = {}
            print("=" * 44)
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            for name, addr, func in items:
                try:
                    values[name] = read_float(addr, func)
                    print(f"{name:<22}: {values[name]:.4f}")
                except Exception as e:
                    values[name] = None
                    print(f"{name:<22}: {e}")

            # Consistency check: S should be close to sqrt(P^2 + Q^2)
            p = values.get("Active Power (W)")
            q = values.get("Reactive Power (var)")
            s = values.get("Apparent Power (VA)")
            if None not in (p, q, s) and s:
                calc_s = (p ** 2 + q ** 2) ** 0.5
                print(f"{'Check sqrt(P2+Q2)':<22}: {calc_s:.2f} (S = {s:.2f})")

            print("=" * 44)

            if writer:
                row = [datetime.now().isoformat(timespec="seconds")]
                row += ["" if values[n] is None else f"{values[n]:.4f}" for n in names]
                writer.writerow(row)
                csv_file.flush()

            time.sleep(POLL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        if csv_file:
            csv_file.close()
        client.close()


if __name__ == "__main__":
    main()
