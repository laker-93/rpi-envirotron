import serial
from threading import Thread
import time
import pynmea2

port = "/dev/serial0"

class GPS:
    def __init__(self):
        self.ser = serial.Serial(port, 9600, 8, 'N', 1, timeout=1)
        self.ser.reset_input_buffer()

    @staticmethod
    def handle_data(data):
        if data.startswith(r'$GNGGA'):
            msg = pynmea2.parse(data)
            print("gngga gps: {}".format(msg))
            return msg
        if data.startswith(r'$GPGGA'):
            msg = pynmea2.parse(data)
            if (msg.latitude, msg.longitude) != (0.0, 0.0):
                return msg
    
    def read_from_port(self, result):
        try:
            data = self.ser.readline().decode()
            if data:
                msg = self.handle_data(data)
                if msg:
                    result[0] = (msg.latitude, msg.longitude)
        except Exception as ex:
            self.ser.close()
            time.sleep(0.2)
            self.ser = serial.Serial(port, 9600, 8, 'N', 1, timeout=1)
            self.ser.reset_input_buffer()
