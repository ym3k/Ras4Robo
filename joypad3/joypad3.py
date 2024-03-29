#!/usr/bin/python3
#
# this module refers to "https://www.usagi1975.com/30jul170722/"
import argparse
from enum import Enum
import signal
import struct
from time import sleep
#import wiringpi as wpi
from drive import gpio_init, Caterpillar, CameraPod, map_axis, deleteDrive

device_path = "/dev/input/js0"

#EVENT_FORMAT = "LhBB"
EVENT_FORMAT = "IhBB"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

L_WHEEL_MIN = 30
R_WHEEL_MIN = 30
L_WHEEL_MAX = 100
R_WHEEL_MAX = 100

AXIS_ABS_MAX = 32767
AXIS_MAX = AXIS_ABS_MAX * 2
# event type
class Type(Enum):
    EV_KEY = 1
    EV_ABS = 2
    EV_129 = 129
    EV_130 = 130

# keynumber
class Key(Enum):
    X = 0
    A = 1
    B = 2
    Y = 3
    LB = 4
    RB = 5
    LT = 6
    RT = 7
    BACK = 8
    START = 9
    axis_L = 10
    axis_R = 11

class Axis(Enum):
    L_X = 0
    L_Y = 1
    R_X = 2
    R_Y = 3
    Pad_X = 4
    Pad_Y = 5

def term_handler(sig_number, frame):
    deleteDrive(PI)
    exit()

class Joypad():
    def __init__(self, device_path=device_path,host='localhost'):
        global PI
        PI = gpio_init(host)
        self.device_path = device_path
        self.cat = Caterpillar(PI)
        self.cam = CameraPod(PI)
        self.Move_ctrl = self.cat.move
        self.pod_ctrl  = self.cam.move
        self.wheel_l = 0
        self.wheel_r = 0
        self.axis_l_x = 0
        self.axis_l_y = 0

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
        while True:
            try:
                with open(device_path, "rb") as device:
                    self.device = device
                    self.event = device.read(EVENT_SIZE)
                    while self.event:
                        (_, js_val, js_type, js_num) = \
                            struct.unpack(EVENT_FORMAT, self.event)
                        self.print_event(js_val, js_type, js_num)
                        if Type(js_type) == Type.EV_KEY:
                            if js_val == 1:
                                if Key(js_num) == Key.axis_R:
                                    self.pod_ctrl("BRK")
                                elif Key(js_num) == Key.axis_L:
                                    self.Move_ctrl("BRK")
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
                        self.event = self.device.read(EVENT_SIZE)
            except FileNotFoundError:
                # maybe can not open "/dev/input/js0"
                # wait 5s, then try again
                print('cant open js0, try once more.')
                sleep(5)

    def print_event(self, js_val, js_type, js_num):
            print("{0}, {1}, {2}".format(js_type, js_num, js_val))
            #print("{0}, {1}, {2}".format(Type(js_type).name, js_num, js_val))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='pigpiod', required=False)
    parser.set_defaults(host='localhost')
    args = parser.parse_args()

    # wait 10 seconds fpr system ready
    sleep(10)
    joypad = Joypad(host=args.host)
    signal.signal(signal.SIGTERM, term_handler)
    try:
        joypad.loop()
    except KeyboardInterrupt:
        deleteDrive()
