import pigpio
import time
import struct
import sys
import crcmod
from binascii import hexlify


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

PIGPIO_HOST = '::1'
PIGPIO_HOST = '127.0.0.1'

I2C_SLAVE = 0x61
I2C_BUS = 1

class Pid:
    def __init__(self):
        self.pi = pigpio.pi(PIGPIO_HOST)
    def connect(self):
        if not self.pi.connected:
            eprint("no connection to pigpio daemon at " + PIGPIO_HOST + ".")
            exit(1)
        try:
            self.pi.i2c_close(0)
        except pigpio.error:
            # No active handles
            pass

    def get_pid(self):
        return self.pi

class SCD30:
    def __init__(self, pid):
        self.pid = pid
        try:
            self.handle = self.pid.i2c_open(I2C_BUS, I2C_SLAVE)
        except:
            eprint("i2c open failed")
            exit(1)

    def close(self):
        self.pid.i2c_close(self.handle)

    def read_n_bytes(self, n):
      try:
          (count, data) = self.pid.i2c_read_device(self.handle, n)
      except:
          eprint("error: i2c_read failed")
          exit(1)
      if count == n:
          return data
      else:
          eprint("error: read measurement interval didnt return " + str(n) + "B")
          return False

    def i2c_write(self, data):
      try:
          self.pid.i2c_write_device(self.handle, data)
      except:
          eprint("error: i2c_write failed")
          return -1
      return True


    def set_interval(self, interval):
      eprint("setting interval to 2")
      ret = i2c_write([0x46, 0x00, 0x00, bytes([interval]), 0xE3])
      if ret == -1:
        exit(1)
      return self.read_meas_interval()

    def read_meas_interval(self):
      ret = self.i2c_write([0x46, 0x00])
      if ret == -1:
          return -1
    
      try:
        (count, data) = self.pid.i2c_read_device(self.handle, 3)
      except:
        eprint("error: i2c_read failed")
        exit(1)
    
      if count == 3:
        if len(data) == 3:
          interval = int(data[0])*256 + int(data[1])
          return interval
        else:
          eprint("error: no array len 3 returned, instead " + str(len(data)) + "type: " + str(type(data)))
      else:
        "error: read measurement interval didnt return 3B"
      
      return -1

    def _is_ready(self):
        """
        Blocks until sensor has data
        """
        while True:
            ret = self.i2c_write([0x02, 0x02])
            if ret == -1:
                eprint("error writing")
                exit(1)
            data = self.read_n_bytes(3)
            if data == False:
                time.sleep(0.1)
                continue
            if data[1] == 1:
                break
            else:
                time.sleep(0.1)
        
    def get_readings(self):
        self._is_ready()
        self.i2c_write([0x03, 0x00])
        data = self.read_n_bytes(18)
        
        if data == False:
            exit(1)
        struct_co2 = struct.pack('>BBBB', data[0], data[1], data[3], data[4])
        float_co2 = struct.unpack('>f', struct_co2)[0]
        try:
            int_co2 = int(float_co2)
        except ValueError:
            print("got value error: {}".format(int_co2))
        struct_T = struct.pack('>BBBB', data[6], data[7], data[9], data[10])
        float_T = round(struct.unpack('>f', struct_T)[0], 2)
        struct_rH = struct.pack('>BBBB', data[12], data[13], data[15], data[16])
        float_rH = round(struct.unpack('>f', struct_rH)[0], 2)
        
        return (float_T, float_rH, int_co2)
