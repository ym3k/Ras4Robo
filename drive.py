#!/usr/bin/python3

import wiringpi as wpi


# set GPIO Pin
# drive motor
R_IN1 = 18
R_IN2 = 23
L_IN1 = 17
L_IN2 = 27
M_SETUP = 22
# camera pod
POD_V = 24
POD_H = 25

# set PIN Mode
INPUT = 0
OUTPUT = 1

# set Vcc
LOW = 0
HIGH = 1

# set Servo OFFSET
OFFSET_MS = 3
SERVO_MIN_MS = 5 + OFFSET_MS
SERVO_MAX_MS = 25 + OFFSET_MS

# camera pod axes degree
POD_V_MIN_DEG = 0
POD_V_MAX_DEG = 45
POD_H_MIN_DEG = 0
POD_H_MAX_DEG = 180

def map_axis(value,fromLow,fromHigh,toLow,toHigh):
    return int((toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow)

def servoWrite(pin, angle, min=0, max=90):
    if (angle > max):
        angle = max
    elif (angle < min):
        angle =min
    wpi.softPwmWrite(pin, map_axis(angle, min,max, SERVO_MIN_MS, SERVO_MAX_MS))

class caterpillar():
    def __init__(self, wpi):
        wpi.wiringPiSetupGpio()

        wpi.pinMode(R_IN1, OUTPUT)
        wpi.pinMode(R_IN2, OUTPUT)
        wpi.pinMode(L_IN1, OUTPUT)
        wpi.pinMode(L_IN2, OUTPUT)
        wpi.pinMode(M_SETUP, OUTPUT)

        wpi.softPwmCreate(R_IN1, 0, 100)
        wpi.softPwmCreate(R_IN2, 0, 100)
        wpi.softPwmCreate(L_IN1, 0, 100)
        wpi.softPwmCreate(L_IN2, 0, 100)
    
    def Move_ctrl(self, com, val=0):
        wpi.digitalWrite(M_SETUP, HIGH)

        if com == "R_FW":
            wpi.softPwmWrite(R_IN1, val)
            wpi.softPwmWrite(R_IN2, 0)
        elif com == "R_RW":
            wpi.softPwmWrite(R_IN1, 0)
            wpi.softPwmWrite(R_IN2, val)
        elif com == "L_FW":
            wpi.softPwmWrite(L_IN1, val)
            wpi.softPwmWrite(L_IN2, 0)
        elif com == "L_RW":
            wpi.softPwmWrite(L_IN1, 0)
            wpi.softPwmWrite(L_IN2, val)
        elif com == "R_STOP":
            wpi.softPwmWrite(R_IN1, 0)
            wpi.softPwmWrite(R_IN2, 0)
        elif com == "L_STOP":
            wpi.softPwmWrite(L_IN1, 0)
            wpi.softPwmWrite(L_IN2, 0)
        elif com == "BRK":
            wpi.softPwmWrite(R_IN1, 100)
            wpi.softPwmWrite(R_IN2, 100)
            wpi.softPwmWrite(L_IN1, 100)
            wpi.softPwmWrite(L_IN2, 100)
            wpi.delay(500)
            wpi.softPwmWrite(R_IN1, 0)
            wpi.softPwmWrite(R_IN2, 0)
            wpi.softPwmWrite(L_IN1, 0)
            wpi.softPwmWrite(L_IN2, 0)
            wpi.digitalWrite(M_SETUP, LOW)

class camera_pod():
    def __init__(self,wpi):
        wpi.wiringPiSetupGpio()

        wpi.pinMode(POD_H, OUTPUT)
        wpi.pinMode(POD_V, OUTPUT)

        wpi.softPwmCreate(POD_H, 0, 200)
        wpi.softPwmCreate(POD_V, 0, 200)
    
    def Move_ctrl(self, com, val=0):
        if com == "POD_V":
            servoWrite(POD_V,val, POD_V_MIN_DEG, POD_V_MAX_DEG)
        elif com == "POD_H":
            servoWrite(POD_H,val, POD_H_MIN_DEG, POD_H_MAX_DEG)

if __name__ == "__main__":
    ras4move = caterpillar(wpi)
    ras4cam  = camera_pod(wpi)

    for i in range(0,0):
        ras4move.Move_ctrl("R_FW", 80)
        ras4move.Move_ctrl("L_FW", 80)
        wpi.delay(2000)
        ras4move.Move_ctrl("R_RW", 80)
        ras4move.Move_ctrl("L_RW", 80)
        wpi.delay(1000)
        ras4move.Move_ctrl("BRK")
        wpi.delay(1000)
        print(i, end=" ")

    for i in range(0, 180):
        ras4cam.Move_ctrl("POD_V",i)
        ras4cam.Move_ctrl("POD_H",i)
        wpi.delay(2000)