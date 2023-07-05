#!/usr/bin/python3

import argparse
import numpy as np
import os
import paho.mqtt.client as mqtt
import signal
import struct
import sys
import ydlidar

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_TOPIC = "lidar1"

SERIAL_PORT = "/dev/ttyUSB0"
LASER_POINTS = 160 # YDLiDAR GS2 contains 160 scan points
SCAN_PACKET_FORMAT = "Q" + "f" * LASER_POINTS * 3
# format: {
#   timestamp: uint64_t
#   laserpoint: (angle: float, range: float, intensity: float)
#   ....  x 160 points
# }

class LidarPublisher():
    def __init__(self, serial=SERIAL_PORT, host=MQTT_HOST, port=MQTT_PORT):
        self.serial = serial
        self.host = host
        self.port = port
        ret = self.__ydinit__()
        if not ret:
            raise ValueError("can't initialize LiDAR")
        self.__mqttinit__(self.host, self.port)

    def __ydinit__(self) -> bool:
        # setup YDLiDAR GS2
        ydlidar.os_init();
        laser = ydlidar.CYdLidar();
        ports = ydlidar.lidarPortList();
        if self.serial not in ports.values():
            raise ValueError("can't find lidar device at {}".format(port))
        else:
            port = self.serial
        laser.setlidaropt(ydlidar.LidarPropSerialPort, port);
        laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 921600);
        laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_GS);
        laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL);
        laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0);
        laser.setlidaropt(ydlidar.LidarPropSampleRate, 20);
        laser.setlidaropt(ydlidar.LidarPropSingleChannel, False);

        self.laser = laser
        ret = laser.initialize();
        if ret:
            self.laserOn = laser.turnOn();
            self.scan = ydlidar.LaserScan()
            return True
        else:
            return False

    def start(self):
        ''' LiDAR start '''
        self.mqttc.loop_start()
        while self.laserOn and ydlidar.os_isOk() :
            r = self.laser.doProcessSimple(self.scan);
            if r:
                #print("Scan received[",self.scan.stamp,"]:",self.scan.points.size(),"ranges is [",1.0/self.scan.config.scan_time,"]Hz");
                data_array = np.array([(s.angle, s.range, s.intensity) for s in self.scan.points]).flatten()
                packed = struct.pack(SCAN_PACKET_FORMAT, self.scan.stamp, *data_array)
                self.mqttc.publish(MQTT_TOPIC, packed)
            else :
                print("Failed to get Lidar Data.")
        self.destory()

    def destory(self):
        self.mqttc.loop_stop()
        self.__mqttclose()
        self.laser.turnOff();
        self.laser.disconnecting();

    def stop(self):
        ''' LiDAR stop '''
        print("stop lidar...")
        self.laserOn = False
        self.destory()

    def restart(self):
        ''' LiDAR restart '''
        ret = self.__ydinit__()
        if not ret:
            raise ValueError("can't initialize LiDAR")
        self.__mqttinit__(self.host, self.port)
        self.start()

    def __mqttinit__(self, host, port) -> None:
        self.mqttc = mqtt.Client()
        self.mqttc.on_publish = self.__on_publish
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.connect(host, port, MQTT_KEEPALIVE)
        print("connected to mqtt broker")

    def __on_connect(self, mqttc, obj, flags, rc):
        print("result code: " + str(rc))

    def __on_publish(self, mqttc, obj, result):
        print("publish: {0}".format(result))

    def __mqttclose(self) -> int:
        print("close connection to mqtt broker")
        self.mqttc.disconnect()
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False)
    parser.add_argument('--port', required=False)
    parser.add_argument('--lidarport', required=False)
    parser.set_defaults(host=MQTT_HOST)
    parser.set_defaults(port=MQTT_PORT)
    parser.set_defaults(lidarport=SERIAL_PORT)
    args = parser.parse_args()

    gs2 = LidarPublisher()

    def term_handler(signumber, frame):
        _ = gs2.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    gs2.start()
