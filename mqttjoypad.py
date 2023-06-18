#!/usr/bin/python3

import argparse
import paho.mqtt.client as mqtt
import signal
import struct
import sys
import time

from defines import EVENT_FORMAT, EVENT_SIZE, AXIS_ABS_MAX, AXIS_MAX, Type, Key, Axis
from drive import gpio_init, Caterpillar, CameraPod, map_axis, deleteDrive

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

MQTT_TOPIC = 'drive1'

device_path = "/dev/input/js0"

class Mqttjoypad():
    def __init__(self, host, port, joypad):
        self.mqttc = mqtt.Client()
        self.mqttc.on_pulish = self.on_publish
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect(host, port, MQTT_KEEPALIVE)
        self.device_path = joypad
        self.started = True

    def close(self):
        self.started = False
        print("close connection to mqtt broker")
        self.mqttc.disconnect()
        return 0

    def on_connect(self, mqttc, obj, flags, rc):
        print("result code: " + str(rc))

    def on_publish(self, mqttc, obj, result):
        print("publish: {0}".format(result))

    def loop(self):
        while True:
            try:
                with open(self.device_path, "rb") as device:
                    while self.started:
                        event = device.read(EVENT_SIZE)
                        self.mqttc.publish(MQTT_TOPIC, event)
                break

            except FileNotFoundError:
                # maybe can not open "/dev/input/js0"
                # wait 5s, then try again
                print('cant open js0, try once more.')
                time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False)
    parser.add_argument('--port', required=False)
    parser.add_argument('--joypad', required=False)
    parser.set_defaults(host=MQTT_HOST)
    parser.set_defaults(port=MQTT_PORT)
    parser.set_defaults(joypad=device_path)
    args = parser.parse_args()

    mqttjoypad = Mqttjoypad(host=args.host, port=args.port,
                            joypad=args.joypad)

    def term_handler(signumber, frame):
        _ = mqttjoypad.close()
        time.sleep(5)
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)

    try:
        mqttjoypad.loop()
    except KeyboardInterrupt:
        mqttjoypad.close()
        sys.exit(0)
