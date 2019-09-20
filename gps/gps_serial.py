import serial
from threading import Thread
import pynmea2

port = "/dev/serial0"

class GPS:
    def __init__(self):
        self.ser = serial.Serial(port, 9600, 8, 'N', 1, timeout=1)
        self.ser.reset_input_buffer()

    @staticmethod
    def handle_data(data):
        if data.startswith(r'$GNGGA') or data.startswith(r'$GPGGA'):
            msg = pynmea2.parse(data)
            return msg.latitude, msg.longitude
    
    def read_from_port(self, result):
        try:
            data = self.ser.readline().decode()
            if data:
                msg = self.handle_data(data)
                if msg:
                    result[0] = msg
        except Exception as ex:
            self.ser.close()
            self.ser = serial.Serial(port, 9600, 8, 'N', 1, timeout=1)
            self.ser.reset_input_buffer()
