#!/usr/bin/python3

import wiringpi as wpi

WPISETUP = 1
DRIVE_INSTANCES = set()

# set GPIO Pin
# drive motor
R_IN1 = 18
R_IN2 = 23
L_IN1 = 17
L_IN2 = 27
M_SETUP = 22
# camera pod
POD_V = 12
POD_H = 13

# set PIN Mode
INPUT = 0
OUTPUT = 1
PWM_OUTPUT = wpi.GPIO.PWM_OUTPUT

# set Vcc
LOW = 0
HIGH = 1

# set PWM setting
PWM_RANGE = 1024
PWM_CLOCK = 375

# set Servo OFFSET
# for SG90 Servo, 0deg=31ms, 180deg=135ms
SERVO_MIN_MS = 31
SERVO_MAX_MS = 135
# available degree for SG90
SERVO_MIN_DEG = 0
SERVO_MAX_DEG = 180

# camera pod axes degree
POD_V_MIN_DEG = -21 
POD_V_MAX_DEG = 90
POD_H_MIN_DEG = 0
POD_H_MAX_DEG = 180

def map_axis(value,fromLow,fromHigh,toLow,toHigh):
    return int((toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow)

def servoWrite(pin, angle, mindeg=0, maxdeg=90):
    offset = 0 - mindeg
    mindeg = offset + mindeg
    maxdeg = offset + maxdeg
    angle = offset + angle
    if (angle > maxdeg):
        angle = maxdeg
    elif (angle < mindeg):
        angle =mindeg
    wpi.pwmWrite(pin, map_axis(angle, SERVO_MIN_DEG, SERVO_MAX_DEG, SERVO_MIN_MS, SERVO_MAX_MS))

def servoWriteV(pin, angle, mindeg=0, maxdeg=90):
    # this projects Vetial Servo is not apply spec for SG90
    # dam patch...
    V_SERVO_MIN_MS = 28
    V_SERVO_MAX_MS = 81
    offset = 0 - mindeg
    mindeg = offset + mindeg
    maxdeg = offset + maxdeg
    angle = offset + angle
    if (angle > maxdeg):
        angle = maxdeg
    elif (angle < mindeg):
        angle =mindeg
    wpi.pwmWrite(pin, map_axis(angle, 0, 111, V_SERVO_MIN_MS, V_SERVO_MAX_MS))

def deleteDrive():
    for i in DRIVE_INSTANCES:
        i.Destroy()

class caterpillar():
    def __init__(self, wpi):
        global DRIVE_INSTANCES
        if len(DRIVE_INSTANCES) == 0:
            # already set up wiringPi
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

        DRIVE_INSTANCES.add(self)
    
    def Move(self, com, val=0):
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
    
    def Test(self, times=3):
        print("motor test")
        for i in range(0,times):
            self.Move("R_FW", 80)
            self.Move("L_FW", 80)
            wpi.delay(2000)
            self.Move("R_RW", 80)
            self.Move("L_RW", 80)
            wpi.delay(1000)
            self.Move("BRK")
            wpi.delay(1000)
            print(i, end=" ")

    def Destroy(self):
        self.Move("BRK")
        wpi.pinMode(R_IN1, INPUT)
        wpi.pinMode(R_IN2, INPUT)
        wpi.pinMode(L_IN1, INPUT)
        wpi.pinMode(L_IN2, INPUT)
        wpi.pinMode(M_SETUP, INPUT)


class camera_pod():
    def __init__(self,wpi):
        global DRIVE_INSTANCES
        if len(DRIVE_INSTANCES) == 0:
            # already set up wiringPi
            wpi.wiringPiSetupGpio()

        wpi.pinMode(POD_H, PWM_OUTPUT)
        wpi.pinMode(POD_V, PWM_OUTPUT)

        wpi.pwmSetMode(wpi.GPIO.PWM_MODE_MS)
        wpi.pwmSetRange(PWM_RANGE)
        wpi.pwmSetClock(PWM_CLOCK)

        DRIVE_INSTANCES.add(self)
    
        self.lock=True
    
    def Move(self, com, val=0):
        if self.lock == False:
            if com == "POD_V":
                servoWriteV(POD_V,val, POD_V_MIN_DEG, POD_V_MAX_DEG)
            elif com == "POD_H":
                servoWrite(POD_H,val, POD_H_MIN_DEG, POD_H_MAX_DEG)
        if com == "BRK":
            if self.lock:
                self.lock = False
            else:
                self.Stop()
    
    def Stop(self, lock=True):
        wpi.pwmWrite(POD_H, 0)
        wpi.pwmWrite(POD_V, 0)
        self.lock = lock


    def Test(self):
        self.lock = False
        self.Move("POD_V", -27)
        self.Move("POD_H", 0)
        wpi.delay(1000)
        self.Move("POD_H", 90)
        self.Move("POD_V", 45)
        wpi.delay(1000)
        self.Move("POD_H", 180)
        self.Move("POD_V", 90)
        wpi.delay(1000)
        self.Move("POD_H", 90)
        self.Move("POD_V", 0)
        wpi.delay(1000)
        self.Stop()

    def Destroy(self):
        self.lock = False
        self.Move("POD_H", 90)
        self.Move("POD_V", 0)
        wpi.delay(1000)
        self.Stop()
        wpi.pinMode(POD_H, INPUT)
        wpi.pinMode(POD_V, INPUT)

if __name__ == "__main__":
    ras4move = caterpillar(wpi)
    ras4cam  = camera_pod(wpi)

    #ras4move.Test()
    ras4cam.Test()

    deleteDrive()
