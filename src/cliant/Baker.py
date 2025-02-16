import serial
import serial_ctrl

from time import sleep

class baker:
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.close()
        self.ser.baudrate = 115200
        self.ser.timeout = 5       # タイムアウトの時間
    def __del__(self):
        if self.ser != None:
            self.ser.close()
    def address_set(self,start_address):
        instruction = "@{:0>6X}\n".format(start_address)
        self.ser.write(instruction.encode('ascii'))
        return self.ser.readline().strip().decode('UTF-8')
    def read(self):
        instruction = "R\n"
        self.ser.write(instruction.encode('ascii'))
        line = self.ser.readline().strip().decode('UTF-8')
        return int(line,16)
    def read_area(self,start_address,end_address):
        result = list()
        
        self.address_set(start_address)
        for count in range(end_address-start_address+1):
            result.append(self.read())
        return result
    def write(self,data):
        instruction = "W{:0>2X}\n".format(data)
        self.ser.write(instruction.encode('ascii'))
        line = self.ser.readline().strip().decode('UTF-8')
        return int(line,16)
    def write_area(self,start_address,data):
        result = list()
        
        self.address_set(start_address)
        for dt in data:
            result.append(self.write(dt))
        return result
    def erase_all(self):
        instruction = "D\n"
        self.ser.write(instruction.encode('ascii'))
        line = self.ser.readline().strip().decode('UTF-8')
        return int(line,16)
    def device_check(self):
        instruction = "V\n"
        self.ser.write(instruction.encode('ascii'))
        line = self.ser.readline().strip().decode('UTF-8')
        return line

if __name__ == "__main__":
    baker_dev = baker()
    baker_dev.ser.port = serial_ctrl.select_port()
    baker_dev.ser.open()
    sleep(3)
    print(baker_dev.device_check())
    print(baker_dev.read_area(0x00,0x0F))
    print("=========")
    print(baker_dev.write_area(0x00,range(10)))
    print(baker_dev.read_area(0x00,0x0F))