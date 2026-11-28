import serial.tools.list_ports

# DUT serial number
DUT_SERIAL_NUMBER = "20:6E:F1:CC:9C:E4"

DUT_COMPORT = None

# Scan all available COM ports
ports = serial.tools.list_ports.comports()

for port in ports:
    if port.serial_number == DUT_SERIAL_NUMBER:
        DUT_COMPORT = port.device
        break

if DUT_COMPORT:
    print(f"{DUT_COMPORT}")
else:
    print("DUT not found")
