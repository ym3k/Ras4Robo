#!/usr/bin/python3

import numpy as np
import os
import struct
import ydlidar

SERIAL_PORT = "/dev/ttyUSB0"

class YdlidarGS2():
    def __init__(self, serial=SERIAL_PORT):
        ydlidar.os_init();
        laser = ydlidar.CYdLidar();
        ports = ydlidar.lidarPortList();
        if serial not in ports.values():
            raise ValueError("can't find lidar device at {}".format(port))
        else:
            port = serial
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
            self.ret = laser.turnOn();
            self.scan = ydlidar.LaserScan()

    def start(self):
        while self.ret and ydlidar.os_isOk() :
            r = self.laser.doProcessSimple(self.scan);
            if r:
                print("Scan received[",self.scan.stamp,"]:",self.scan.points.size(),"ranges is [",1.0/self.scan.config.scan_time,"]Hz");
                data_array = np.array([(s.angle, s.range, s.intensity) for s in self.scan.points]).flatten()
                packed = struct.pack("Q" + "f" * len(data_array), self.scan.stamp, *data_array)
            else :
                print("Failed to get Lidar Data.")
        self.destory()

    def destory(self):
        self.laser.turnOff();
        self.laser.disconnecting();

if __name__ == "__main__":
    gs2 = YdlidarGS2()
    gs2.start()
