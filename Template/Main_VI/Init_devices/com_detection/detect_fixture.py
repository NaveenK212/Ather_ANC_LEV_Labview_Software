import serial.tools.list_ports
import json
import os


def get_comport_list():
    device={}
    com_ports = serial.tools.list_ports.comports()
    
    for i in com_ports:
        device.update({i.device:i.serial_number})

    cwd=os.getcwd()
    res = []
    # Iterate directory
    for file in os.listdir(cwd):
        # check only text files
        if file.endswith('.json'):
            res.append(file)

    comport={}
    for filename in res:
        f = open (filename, "r")
        data = json.loads(f.read())
        f.close()

        for i in device:
            if device[i] in data.values():
                comport.update({i:device[i]})
        comport.update({1:"COM2"})
        comport.update({2:"COM2"})# need to remove in final testing
        if len(comport)==4:
            break

    # to get in order of deviceaddress
    comport_main=""
    for i in data:
        for j in comport:
            if data[i] == comport[j]:
                comport_main+=j
                continue
        else:
           comport_main+="\n"

    return comport_main



print(get_comport_list())