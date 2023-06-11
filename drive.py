#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
import pigpio

DRIVE_INSTANCES = set()

# set GPIO Pin
# drive motor
R_IN1 = 18
R_IN2 = 23
L_IN1 = 17
L_IN2 = 27
M_SETUP = 22
D_FREQ = 100
D_RANGE = 100
# camera pod
POD_V = 12
POD_H = 13

# set PIN Mode
INPUT = pigpio.INPUT
OUTPUT = pigpio.OUTPUT

# set Vcc
LOW = 0
HIGH = 1

# available degree for SG90
H_SERVO_MIN_DEG = 0
H_SERVO_MAX_DEG = 180
V_SERVO_MIN_DEG = 0
V_SERVO_MAX_DEG = 111
SERVO_FREQ = 50
SERVO_RANGE = 1024

# move range of camera_pod
POD_V_MIN_DEG = -21
POD_V_MAX_DEG = 90
POD_H_MIN_DEG = 0
POD_H_MAX_DEG = 180

# set Servo Offset
# general values are -90=25, +90=135 (0=74), but
# there are individual differences in servos in these values.
# if you replace servo, you must tune the values.
V_SERVO_MIN_MS = 28
V_SERVO_MAX_MS = 81
H_SERVO_MIN_MS = 31
H_SERVO_MAX_MS = 135

def gpio_init():
    return pigpio.pi()

def map_axis(value,fromLow,fromHigh,toLow,toHigh):
    return int((toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow)

def deleteDrive(pi):
    for i in  DRIVE_INSTANCES:
        i.destroy()
    pi.stop()

class Servo():
    def __init__(self, pi, pin, pod_mindeg, pod_maxdeg, 
            servo_mindeg=0, servo_maxdeg=180, minms=25, maxms=135):
        self.pi = pi
        self.pin = pin
        self.pod_mindeg = pod_mindeg
        self.pod_maxdeg = pod_maxdeg
        self.servo_mindeg = servo_mindeg
        self.servo_maxdeg = servo_maxdeg
        self.minms = minms
        self.maxms = maxms

        pi.set_mode(pin, OUTPUT)
        pi.set_PWM_frequency(pin, SERVO_FREQ)
        pi.set_PWM_range(pin, SERVO_RANGE)

    def write(self, angle):
        wpi = self.pi
        offset = 0 - self.pod_mindeg
        mindeg = offset + self.pod_mindeg
        maxdeg = offset + self.pod_maxdeg
        angle = offset + angle
        if (angle > maxdeg):
            angle = maxdeg
        elif (angle < mindeg):
            angle = mindeg
        wpi.set_PWM_dutycycle(self.pin, map_axis(angle, 
                                            self.servo_mindeg, self.servo_maxdeg, 
                                            self.minms, self.maxms))

    def stop(self):
        self.pi.set_PWM_dutycycle(self.pin, 0)

    
class Caterpillar():
    def __init__(self, pi):
        for i in [R_IN1, R_IN2, L_IN1, L_IN2]:
            pi.set_mode(i, OUTPUT)
            pi.set_PWM_frequency(i, D_FREQ)
            pi.set_PWM_range(i, D_RANGE)

        pi.set_mode(M_SETUP, OUTPUT)
        self.pi = pi

        DRIVE_INSTANCES.add(self)


    def move(self, com, val=0):
        wpi = self.pi
        wpi.write(M_SETUP, HIGH)

        if com == "R_FW":
            wpi.set_PWM_dutycycle(R_IN1, val)
            wpi.set_PWM_dutycycle(R_IN2, 0)
        elif com == "R_RW":
            wpi.set_PWM_dutycycle(R_IN1, 0)
            wpi.set_PWM_dutycycle(R_IN2, val)
        elif com == "L_FW":
            wpi.set_PWM_dutycycle(L_IN1, val)
            wpi.set_PWM_dutycycle(L_IN2, 0)
        elif com == "L_RW":
            wpi.set_PWM_dutycycle(L_IN1, 0)
            wpi.set_PWM_dutycycle(L_IN2, val)
        elif com == "R_STOP":
            wpi.set_PWM_dutycycle(R_IN1, 0)
            wpi.set_PWM_dutycycle(R_IN2, 0)
        elif com == "L_STOP":
            wpi.set_PWM_dutycycle(L_IN1, 0)
            wpi.set_PWM_dutycycle(L_IN2, 0)
        elif com == "BRK":
            wpi.set_PWM_dutycycle(R_IN1, 100)
            wpi.set_PWM_dutycycle(R_IN2, 100)
            wpi.set_PWM_dutycycle(L_IN1, 100)
            wpi.set_PWM_dutycycle(L_IN2, 100)
            sleep(0.5)
            wpi.set_PWM_dutycycle(R_IN1, 0)
            wpi.set_PWM_dutycycle(R_IN2, 0)
            wpi.set_PWM_dutycycle(L_IN1, 0)
            wpi.set_PWM_dutycycle(L_IN2, 0)
            wpi.write(M_SETUP, LOW)

    def test(self, times=3):
        print("motor test")
        for i in range(0,times):
            self.move("R_FW", 80)
            self.move("L_FW", 80)
            sleep(2)
            self.move("R_RW", 80)
            self.move("L_RW", 80)
            sleep(1)
            self.move("BRK")
            sleep(1)
            print(i, end=" ")

    def destroy(self):
        self.move("BRK")
        wpi = self.pi
        wpi.set_mode(R_IN1, INPUT)
        wpi.set_mode(R_IN2, INPUT)
        wpi.set_mode(L_IN1, INPUT)
        wpi.set_mode(L_IN2, INPUT)
        wpi.set_mode(M_SETUP, INPUT)

class CameraPod():
    def __init__(self,pi):
        self.pod_v = Servo(pi, POD_V, POD_V_MIN_DEG, POD_V_MAX_DEG,
                                 V_SERVO_MIN_DEG, V_SERVO_MAX_DEG, 
                                 V_SERVO_MIN_MS, V_SERVO_MAX_MS)
        self.pod_h = Servo(pi, POD_H, POD_H_MIN_DEG, POD_H_MAX_DEG,
                                 H_SERVO_MIN_DEG, H_SERVO_MAX_DEG, 
                                 H_SERVO_MIN_MS, H_SERVO_MAX_MS)
        DRIVE_INSTANCES.add(self)
        self.lock=True

    def move(self, com, angle=0):
        if self.lock == False:
            if com == "POD_V":
                self.pod_v.write(angle)
            elif com == "POD_H":
                self.pod_h.write(angle)
        if com == "BRK":
            if self.lock:
                self.lock = False
            else:
                self.stop()

    def stop(self, lock=True):
        self.pod_v.stop()
        self.pod_h.stop()
        self.lock = lock

    def test(self):
        self.lock = False
        self.move("POD_V", -27)
        self.move("POD_H", 0)
        sleep(1)
        self.move("POD_H", 90)
        self.move("POD_V", 45)
        sleep(1)
        self.move("POD_H", 180)
        self.move("POD_V", 90)
        sleep(1)
        self.move("POD_H", 90)
        self.move("POD_V", 0)
        sleep(1)
        self.stop()

    def destroy(self):
        self.lock = False
        self.move("POD_H", 90)
        self.move("POD_V", 0)
        sleep(1)
        self.stop()

if __name__ == "__main__":
    pi = gpio_init()
    ras4move = Caterpillar(pi)
    ras4cam  = CameraPod(pi)

    #ras4move.test()
    ras4cam.test()

    deleteDrive(pi)
