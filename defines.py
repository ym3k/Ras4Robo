#!/usr/bin/python3

from enum import Enum
import struct

EVENT_FORMAT = "IhBB"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

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
