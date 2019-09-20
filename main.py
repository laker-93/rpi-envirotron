from scd30.scd30_driver import Pid, SCD30
from gps.gps_serial import GPS
import time

p = Pid()
p.connect()
pid = p.get_pid()
scd30 = SCD30(pid)

gps = GPS()

# Set the measurement interval to 2s
if scd30.read_meas_interval() != 2:
    print("set interval to 2")
    scd30.set_interval(2)

result = [None]
while True:
    gps.read_from_port(result)
    if scd30.is_ready() and result[0]:
        temp, humidity, co2 = scd30.get_readings()
        lat, lon = result[0]
        json = """[{"topic":"envirotron-pi","payload":[{"measurement":"device_frmpayload_data_co2","tags":{"device_name":"rpi"},"fields":{"value":%d}},{"measurement":"device_frmpayload_data_temperature","tags":{"device_name":"rpi"},"fields":{"value":%f}},{"measurement":"device_frmpayload_data_humidity","tags":{"device_name":"rpi"},"fields":{"value":%f}},{"measurement":"device_frmpayload_data_gps_location","tags":{"device_name":"rpi"},"fields":{"latitude":%f,"longitude":%f}}]}]""" % (co2, temp, humidity, lat, lon)
        print(json)
        with open('/home/pi/envirotron-pi/readings.json', 'w') as results:
            results.write(json)
    else:
        time.sleep(0.1)


