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

L_WHEEL_MIN = 30
R_WHEEL_MIN = 30
L_WHEEL_MAX = 100
R_WHEEL_MAX = 100

#AXIS_ABS_MAX = 32767
#AXIS_MAX = AXIS_ABS_MAX * 2

class Mqttdrive():
    def __init__(self, host, port, gpiohost):
        self.mqttc = mqtt.Client()
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect(host, port, MQTT_KEEPALIVE)
        self.mqttc.subscribe(MQTT_TOPIC)

        self.gpio = gpio_init(gpiohost)
        self.cat = Caterpillar(self.gpio)
        self.cam = CameraPod(self.gpio)
        self.Move_ctrl = self.cat.move
        self.pod_ctrl  = self.cam.move
        self.wheel_l = 0
        self.wheel_r = 0
        self.axis_l_x = 0
        self.axis_l_y = 0

    def close(self):
        print("close connection to mqtt broker")
        self.mqttc.disconnect()
        print("close gpio")
        return deleteDrive(self.gpio)

    def on_connect(self, mqttc, obj, flags, rc):
        print("result code: " + str(rc))

    def on_message(self, mqttc, obj, msg):
        (_, js_val, js_type, js_num) = \
                struct.unpack(EVENT_FORMAT, msg.payload)
        print("{0}, {1}, {2}".format(js_type, js_num, js_val))
        if Type(js_type) == Type.EV_KEY:
            try:
                if Key(js_num) == Key.axis_R:
                    if js_val == 1:
                        self.pod_ctrl("BRK")
                elif Key(js_num) == Key.A:
                    if js_val == 1:
                        print("BRK_ON")
                        self.Move_ctrl("BRK_ON")
                    elif js_val == 0:
                        print("BRK_OFF")
                        self.Move_ctrl("BRK_OFF")
                        self.update_run()
            except ValueError:
                print("Button {0} is not defined".format(js_num))
        elif Type(js_type) == Type.EV_ABS:
            if Axis(js_num) == Axis.R_X:
                ax_r_x = (js_val * -1 ) + AXIS_ABS_MAX
                pod_angle_h = map_axis(ax_r_x, 0, AXIS_MAX, 0, 180)
                self.pod_ctrl("POD_H", pod_angle_h)
            if Axis(js_num) == Axis.R_Y:
                ax_r_y = (js_val * -1 ) + AXIS_ABS_MAX
                pod_angle_v = map_axis(ax_r_y, 0, AXIS_MAX, -90, 90)
                self.pod_ctrl("POD_V", pod_angle_v)
            if Axis(js_num) == Axis.L_Y:
                self.axis_l_y = js_val
                self.update_run()
            if Axis(js_num) == Axis.L_X:
                self.axis_l_x = js_val
                self.update_run()

    def run(self):
        speed_l = map_axis(abs(self.wheel_l), 0, AXIS_ABS_MAX, L_WHEEL_MIN, L_WHEEL_MAX)
        speed_r = map_axis(abs(self.wheel_r), 0, AXIS_ABS_MAX, R_WHEEL_MIN, R_WHEEL_MAX)
        print("MOVE: {0}, {1}".format(speed_l, speed_r))
        if self.wheel_l < 0:
            self.Move_ctrl("L_FW", speed_l)
        elif self.wheel_l > 0:
            self.Move_ctrl("L_RW", speed_l)
        else:
            self.Move_ctrl("L_STOP")
        if self.wheel_r < 0:
            self.Move_ctrl("R_FW", speed_r)
        elif self.wheel_r > 0:
            self.Move_ctrl("R_RW", speed_r)
        else:
            self.Move_ctrl("R_STOP")

    def update_run(self):
        if self.axis_l_x > 0:
            self.wheel_l = self.axis_l_y
            if self.axis_l_y <= 0:
                # forward, right or turn right
                self.wheel_r = self.axis_l_y + self.axis_l_x
            else:
                # backword, right
                self.wheel_r = self.axis_l_y - self.axis_l_x
        elif self.axis_l_x < 0:
            self.wheel_r = self.axis_l_y
            if self.axis_l_y <= 0:
                # forward, left or turn left
                self.wheel_l = self.axis_l_y - self.axis_l_x
            else:
                # backword, left
                self.wheel_l = self.axis_l_y + self.axis_l_x
        else:
            # straight forword or backward
            self.wheel_l = self.wheel_r = self.axis_l_y
        self.run()

    def loop(self):
        self.mqttc.loop_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False)
    parser.add_argument('--port', required=False)
    parser.add_argument('--gpiohost', required=False)
    parser.set_defaults(host=MQTT_HOST)
    parser.set_defaults(port=MQTT_PORT)
    parser.set_defaults(gpiohost='localhost')
    args = parser.parse_args()

    mqtdrive = Mqttdrive(host=args.host, port=args.port,
                         gpiohost=args.gpiohost)
    def term_handler(signumber, frame):
        _ = mqtdrive.close()
        time.sleep(5)
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)

    try:
        mqtdrive.loop()
    except KeyboardInterrupt:
        mqtdrive.close()
        sys.exit(0)
