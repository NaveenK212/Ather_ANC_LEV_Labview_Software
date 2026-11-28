import struct
import time
import logging
from pymodbus.client import ModbusSerialClient

# Enable Modbus library debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

PORT = "COM7"
BAUDRATE = 9600
SLAVE_ID = 1

REGISTERS = {
    "Voltage": 99,
    "Current": 113,
    "Power Factor": 133,
    "Active Power": 141,
    "Reactive Power": 149,
    "Apparent Power": 157
}

print("=" * 60)
print("ELITE 300 MODBUS COMMUNICATION")
print("=" * 60)

# --------------------------------------------------
# INITIALIZATION
# --------------------------------------------------

print("\n[INIT] Creating Modbus Serial Client")
print(f"[INIT] Port       : {PORT}")
print(f"[INIT] Baud rate  : {BAUDRATE}")
print(f"[INIT] Slave ID   : {SLAVE_ID}")
print(f"[INIT] Data bits  : 8")
print(f"[INIT] Parity     : None")
print(f"[INIT] Stop bits  : 1")
print(f"[INIT] Timeout    : 2 seconds")
print("[INIT] Protocol   : Modbus RTU over RS485")

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=2
)

print("\n[INIT] Sending connection request to serial port...")

if client.connect():

    print("[INIT] SUCCESS - Connected to COM7")
    print("[INIT] Modbus communication session established")

    try:

        print("\n" + "=" * 60)
        print("STARTING PHASE 1 MEASUREMENTS")
        print("=" * 60)

        while True:

            print("\n" + "-" * 60)
            print("[CYCLE] Starting measurement cycle")
            print("-" * 60)

            for name, address in REGISTERS.items():

                print("\n[READ REQUEST]")
                print(f"[READ] Measurement     : {name}")
                print(f"[READ] Slave ID       : {SLAVE_ID}")
                print(f"[READ] Function Code  : 03 (Read Holding Registers)")
                print(f"[READ] Starting Addr  : {address}")
                print(f"[READ] Register Count : 2")

                try:

                    result = client.read_holding_registers(
                        address=address,
                        count=2,
                        device_id=SLAVE_ID
                    )

                    print("[READ] Response received from meter")

                    if result.isError():

                        print("[ERROR] Modbus error response")
                        print(f"[ERROR] Response: {result}")

                        continue

                    regs = result.registers

                    print(f"[RESPONSE] Register 1 : {regs[0]} (0x{regs[0]:04X})")
                    print(f"[RESPONSE] Register 2 : {regs[1]} (0x{regs[1]:04X})")

                    # Word swap
                    print("[CONVERT] Swapping register word order")

                    value = struct.unpack(
                        ">f",
                        struct.pack(">HH", regs[1], regs[0])
                    )[0]

                    print("[CONVERT] Float32 conversion completed")

                    print(f"[RESULT] {name} = {value:.4f}")

                except Exception as e:

                    print(f"[ERROR] Failed to read {name}")
                    print(f"[ERROR] {e}")

            print("\n[CYCLE] Measurement cycle completed")
            print("[CYCLE] Waiting 1 second...")

            time.sleep(1)

    except KeyboardInterrupt:

        print("\n[STOP] User interrupted communication")

    finally:

        print("\n[SHUTDOWN] Closing Modbus connection")

        client.close()

        print("[SHUTDOWN] Serial connection closed")
        print("[SHUTDOWN] Communication terminated")

else:

    print("[INIT ERROR] Unable to connect to COM7")
    print("[INIT ERROR] Check cable, COM port and serial settings")

print("\nProgram ended")
