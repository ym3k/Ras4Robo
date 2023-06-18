#!/usr/bin/python3

import argparse
from enum import Enum
import struct
import paho.mqtt.client as mqtt
import pygame
from pygame.locals import *
import time

from defines import EVENT_FORMAT, EVENT_SIZE, AXIS_ABS_MAX, AXIS_MAX, Type, Key, Axis

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

MQTT_TOPIC = 'drive1'

class PGKey(Enum):
    X = 0
    Y = 1
    A = 2
    B = 3
    LB = 4
    RB = 5
    LT = 6
    RT = 7
    axis_L = 8
    axis_R = 9
    BACK = 10
    START = 11

class MqttPublisher():
    def __init__(self, host, port, topic):
        self.mqttc = mqtt.Client()
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect(host, port, MQTT_KEEPALIVE)
        self.topic = topic
        self.started = True

    def close(self):
        self.started = False
        self.mqttc.loop_stop()
        print("close connection to mqtt broker")
        self.mqttc.disconnect()
        return 0

    def on_connect(self, mqttc, obj, flags, rc):
        print("result code: " + str(rc))

    def on_publish(self, mqttc, obj, result):
        print("publish: {0}".format(result))

    def publish(self, mesg):
        self.mqttc.publish(self.topic, mesg)

    def start(self):
        self.mqttc.loop_start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False)
    parser.add_argument('--port', required=False)
    parser.add_argument('--topic', required=False)
    parser.set_defaults(host=MQTT_HOST)
    parser.set_defaults(port=MQTT_PORT)
    parser.set_defaults(topic=MQTT_TOPIC)
    args = parser.parse_args()

    pygame.init()
    pygame.joystick.init()

    # Assume we have at least one joystick present
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    publisher = MqttPublisher(args.host, args.port, args.topic)
    publisher.start()
    try:
        while True:
            time.sleep(0.01)
            for event in pygame.event.get():
                if event.type == JOYAXISMOTION:
                    event_type = 2  # JS_EVENT_AXIS
                    # pygame event values are in the range -1.0 through 1.0, scale to 16-bit signed int
                    event_value = int(event.value * 32767)
                    packed_event = struct.pack('IhBB', pygame.time.get_ticks(), event_value, event_type, event.axis)
                    publisher.publish(packed_event)
                elif event.type in (JOYBUTTONDOWN, JOYBUTTONUP):
                    event_type = 1  # JS_EVENT_BUTTON
                    if event.type == JOYBUTTONDOWN:
                        event_value = 1
                    else:
                        event_value = 0
                    if PGKey(event.button) == PGKey.A:
                        button_num = Key.A.value
                    elif PGKey(event.button) == PGKey.axis_R:
                        button_num = Key.axis_R.value
                    else:
                        button_num = -1

                    if button_num > 0:
                        packed_event = struct.pack('IhBB', pygame.time.get_ticks(), event_value, event_type, button_num)
                        publisher.publish(packed_event)

                else:
                    print("Other joystick events are not handled in this example")
    finally:
        publisher.close()
        pygame.quit()
