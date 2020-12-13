#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

OFFSE_DUTY = 0.1        #define pulse offset of servo
SERVO_MIN_DUTY = 2.5+OFFSE_DUTY     #define pulse duty cycle for minimum angle of servo
SERVO_MAX_DUTY = 12.5+OFFSE_DUTY    #define pulse duty cycle for maximum angle of servo
servoPinH = 22
servoPinV = 18

def map_axis( value, fromLow, fromHigh, toLow, toHigh):  # map a value from one range to another range
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

class camera_pod():
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)         # use PHYSICAL GPIO Numbering
        GPIO.setup(servoPinH, GPIO.OUT)   # Set servoPin to OUTPUT mode
        GPIO.output(servoPinH, GPIO.LOW)  # Make servoPin output LOW level
        GPIO.setup(servoPinV, GPIO.OUT)   # Set servoPin to OUTPUT mode
        GPIO.output(servoPinV, GPIO.LOW)  # Make servoPin output LOW level

        self.pod_h = GPIO.PWM(servoPinH, 50)     # set Frequece to 50Hz
        self.pod_v = GPIO.PWM(servoPinV, 50)     # set Frequece to 50Hz
        self.pod_h.start(0)                     # Set initial Duty Cycle to 0
        self.pod_v.start(0)                     # Set initial Duty Cycle to 0
    
    def servoWrite(self, angle):      # make the servo rotate to specific angle, 0-180 
        if(angle<0):
            angle = 0
        elif(angle > 180):
            angle = 180
        self.pod_h.ChangeDutyCycle(map_axis(angle,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY)) # map the angle to duty cycle and output it
    
    def servoWriteV(self, angle):      # make the servo rotate to specific angle, 0-180 
        LEVELV = 25
        angle=angle+LEVELV
        if(angle<-0):
            angle = 0
        elif(angle > 90+LEVELV):
            angle = 90+LEVELV
        self.pod_v.ChangeDutyCycle(map_axis(angle,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY)) # map the angle to duty cycle and output it
    
    def loop(self):
        #while True:
        for i in range(0,1):
            for dc in range(0, 181, 1):   # make servo rotate from 0 to 180 deg
                self.servoWrite(dc)     # Write dc value to servo
                self.servoWriteV(dc)     # Write dc value to servo
                time.sleep(0.01)
            time.sleep(0.001)
            for dc in range(180, -1, -1): # make servo rotate from 180 to 0 deg
                self.servoWrite(dc)
                self.servoWriteV(dc)
                time.sleep(0.01)
            time.sleep(0.001)
        self.destroy()

    def destroy(self):
        self.servoWrite(90)
        self.servoWriteV(0)
        time.sleep(2)
        self.pod_h.stop()
        self.pod_v.stop()
        GPIO.cleanup()

if __name__ == '__main__':     # Program entrance
    print ('Program is starting...')
    cam = camera_pod()
    try:
        cam.loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        cam.destroy()
