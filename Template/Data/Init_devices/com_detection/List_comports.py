import serial.tools.list_ports


ports=serial.tools.list_ports.comports()

for i in ports:
    print(str(i.serial_number)+" "+str(i))
