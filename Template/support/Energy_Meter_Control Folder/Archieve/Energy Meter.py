import struct
import time
from pymodbus.client import ModbusSerialClient

PORT = "COM7"
BAUDRATE = 9600
SLAVE_ID = 1

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=2
)

# Candidate register offsets
REGISTERS = {
    "Voltage": 99,
    "Current": 113,
    "Power Factor": 133,
    "Active Power": 141,
    "Reactive Power": 149,
    "Apparent Power": 157
}

def read_float(address):
    result = client.read_holding_registers(
        address=address,
        count=2,
        device_id=SLAVE_ID
    )

    if result.isError():
        return None

    regs = result.registers

    # Word swap based on the voltage reading that worked
    value = struct.unpack(
        ">f",
        struct.pack(">HH", regs[1], regs[0])
    )[0]

    return value


if client.connect():

    print("Connected to ELITE 300")
    print("Reading Phase 1 measurements...\n")

    try:
        while True:

            print("=" * 40)

            for name, address in REGISTERS.items():

                try:
                    value = read_float(address)

                    if value is not None:
                        print(f"{name}: {value:.4f}")
                    else:
                        print(f"{name}: Register error")

                except Exception as e:
                    print(f"{name}: {e}")

            print("=" * 40)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped")

    finally:
        client.close()

else:
    print("Unable to connect")
