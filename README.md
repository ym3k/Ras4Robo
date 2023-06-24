# Ras4Robo

## Features
1. Compatible with Raspberry Pi 3 or Raspberry Pi 4.
2. Enables remote control via a joystick for the following devices connected to the Raspberry Pi's GPIO:
   - Two-wheel operation using two DC motor drivers
   - Pan-tilt function of a Raspberry Pi camera using two servo motors
3. Data acquisition from sensors via i2c or serial communication:
   - Time-of-Flight (ToF) or LiDAR
4. Messaging via MQTT
5. Plans to support ROS2 in the future

## Operating Environment
### OS
- Raspberry Pi OS (64bit)
- Ubuntu 22.04 LTS (64bit)

While it operates on either, Raspberry Pi OS is recommended.

### Devices
- Servo Motors: 2x SG90
- DC Motor Drivers: 2x DRV8835
- Motors: 2x Tamiya Mini 4WD Torque-Tuned 2 Motors
- LiDAR: 1x YLIDAR GS2 (850nm)

## Setup
### Software Installation
Application operations will be managed with Docker Compose. However, pigpiod will be started from the OS.
- Docker
- pigpiod

### Docker Installation
Install Docker as described in the ROS2 documentation [here](https://docs.ros.org/en/foxy/How-To-Guides/Installing-on-Raspberry-Pi.html) and the steps provided [here](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script).

To make sure the 'pi' user can operate Docker, execute the following command:
```
usermod -aG docker $USER
```

### pigpiod Configuration
Make pigpiod accessible from Docker containers running on the host.

Override the systemd startup script with:
```bash
sudo systemctl edit pigpiod.service
```

Then add the following:
```
[Service]
ExecStart=
ExecStart=/usr/bin/pigpiod -n localhost
```
Don't forget the `ExecStart=` on the first line.

### Docker Image Creation
```
docker build -t ras4robo:0.1 .
```

## Starting the Process
```
docker compose up -d
```

## Remote Control from a Host
Thanks to MQTT, movement and camera Pan-Tilt operations can be controlled from a remote PC. To connect a joystick to a remote Windows PC, install:
- Python 3.10 or higher
- pygame

Then run:
```
python joypad_pygame.py --host <hostname>
```
