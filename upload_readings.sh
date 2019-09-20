#!/bin/bash
# Publishes readings.json to mosquitto client running on AWS
/usr/bin/mosquitto_pub -h 52.15.67.191 -p 1883 -t "envirotron-pi" -f /home/pi/envirotron-pi/readings.json
echo "made upload"
