from scd30.scd30_driver import Pid, SCD30
from gps.gps_serial import GPS
import time
import at
from cayennelpp import LppFrame

p = Pid()
p.connect()
pid = p.get_pid()
scd30 = SCD30(pid)

gps = GPS()

lora = at.AT_Master("/dev/ttyACM0")
lora.join()

# Set the measurement interval to 2s
if scd30.read_meas_interval() != 2:
    print("set interval to 2")
    scd30.set_interval(2)

result = [None]
while True:
    gps.read_from_port(result)
    if scd30.is_ready() and result[0]:
        temp, humidity, co2 = scd30.get_readings()
        lat = result[0][0]
        lon = result[0][1]
        print("Temp:", temp)
        print("Humidity:", humidity)
        print("CO2:", co2)
        print("Lat:", lat)
        print("Lon:", lon)
        frame = LppFrame()
        frame.add_temperature(1, temp)
        frame.add_humitidy(2, humidity)
        frame.add_gps(3, lat, lon, 0)
        buffer = frame.bytes()
        print(buffer)
        #lora.send_bytes(99, buffer)
    else:
        time.sleep(0.1)
