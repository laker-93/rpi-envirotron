from scd30.scd30_driver import Pid, SCD30
from gps.gps_serial import GPS

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
lat, lon = (0, 0)
while True:
    temp, humidity, co2 = scd30.get_readings()
    gps.read_from_port(result)
    if result[0]:
        lat, lon = result[0]
        json = """[{"topic":"envirotron-pi","device":"SCD30","temperature":%f,"humidity":%f,"co2":%d,"latitude":%f,"longitude":%f}]""" % (temp, humidity, co2, lat, lon)
        with open('/home/pi/envirotron-pi/readings.json', 'w') as results:
            results.write(json)


