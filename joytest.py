#!/usr/bin/env python

import struct

device_path = "/dev/input/js0"

#EVENT_FORMAT = "LhBB"
EVENT_FORMAT = "IhBB"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)
print(EVENT_SIZE)

with open(device_path, "rb") as device:
    while True:
        event = device.read(EVENT_SIZE)
        if event:
            (_, js_val, js_type, js_num) = struct.unpack(EVENT_FORMAT, event)
            print(js_val, js_type, js_num)
