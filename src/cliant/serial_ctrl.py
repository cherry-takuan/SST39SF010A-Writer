import sys
#sys.path.append("/home/cherry/.local/lib/python2.7/site-packages")
import serial
from serial.tools import list_ports
from time import sleep


def select_port(baudrate=19200):
    ports = list_ports.comports()    # ポートデータを取得
    devices = [info.device for info in ports]
    if len(devices) == 0:
        # シリアル通信できるデバイスが見つからなかった場合
        print("Error: Port not found")
        return None
    else:
        # 複数ポートの場合、選択
        for i in range(len(devices)):
            print(f"input {i:d} open {devices[i]}")
        num = int(input("Please enter the port number:" ))
        return devices[num]