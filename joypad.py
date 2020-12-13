#!/usr/bin/python3

import wiringpi as wpi
from drive import caterpillar, map_axis

#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event0')

#button code variables (change to suit your device)
aBtn = 305
bBtn = 306
xBtn = 304
yBtn = 307

hatX = 16
hatY = 17

axisL_X = 0 
axisL_Y = 1
axisR_X = 2
axisR_Y = 5

axisLB = 314
axisRB = 315

start = 313
back = 312

lBump = 308
rBump = 309

lTrig = 310
rTrig = 311

#prints out device info at start
print(gamepad)

###
# init drive caterpillar

catp = caterpillar(wpi)
Move_ctrl = catp.Move_ctrl 

#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS:
        if event.code == axisL_Y:
            axis_val_L = event.value-127
            L_Y_val = map_axis(abs(axis_val_L),0,128,50,100)
            print("axisL_Y", L_Y_val)
            if axis_val_L < 0:
                Move_ctrl("L_FW", L_Y_val)
            elif axis_val_L > 0:
                Move_ctrl("L_RW", L_Y_val)
            else:
                Move_ctrl("L_STOP")
        if event.code == axisR_Y:
            axis_val_R = event.value-127
            R_Y_val = map_axis(abs(event.value-127),0,128,50,100)
            print("axisR_Y", R_Y_val)
            if axis_val_R < 0:
                Move_ctrl("R_FW", R_Y_val)
            elif axis_val_R > 0:
                Move_ctrl("R_RW", R_Y_val)
            else:
                Move_ctrl("R_STOP")
       
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == yBtn:
                print("Y")
            elif event.code == bBtn:
                print("B")
            elif event.code == aBtn:
                print("A")
            elif event.code == xBtn:
                print("X")

            elif event.code == start:
                print("start")
            elif event.code == back:
                print("back")

            elif event.code == axisLB or event.code == axisRB:
                Move_ctrl("BRK")
    
            elif event.code == lBump:
                print("left bumper")
            elif event.code == rBump:
                print("right bumper")
            
            elif event.code == lTrig:
                print("left triger")
            elif event.code == rTrig:
                print("right triger")
