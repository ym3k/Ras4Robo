# Ras4Robo

## Features
1. Runs on Raspberry Pi 3 or Raspberry Pi 4.
2. Remote control of the following devices connected to the Raspberry Pi's GPIO from a joystick:
    - 2-wheel control by two DC motor drivers
    - Pan-Tilt of the Raspberry Pi camera by two servo motors
3. Collection of values from sensors via i2c/serial communication:
    - Time-of-Flight (ToF) or LiDAR
4. Messaging via MQTT
5. Plans to support ROS2 in the future

## Operating Environment
### OS
- Raspberry Pi OS (64bit)
- Ubuntu 22.04 LTS(64bit)

While it operates on either, Raspberry Pi OS is recommended.

## Setup
### Software Installation
The application will be managed using Docker Compose. However, pigpiod will be run directly on the OS.
- Docker
- pigpiod

### Docker Installation
Install Docker as described in the ROS2 documentation [here](https://docs.ros.org/en/foxy/How-To-Guides/Installing-on-Raspberry-Pi.html) and the steps provided [here](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script).

Ensure the 'pi' user has the ability to operate Docker by executing the following command:
```
usermod -aG docker $USER
```

### pigpiod Setup
Configure pigpiod to be accessible from Docker containers running on the host.

Override the systemd startup script.
```bash
sudo systemctl edit pigpiod.service
```

Add the following content.
```
[Service]
ExecStart=
ExecStart=/usr/bin/pigpiod -n localhost
```
Don't forget to write `ExecStart=` on the first line.

### Docker Image Creation
```
docker build -t ras4robo:0.1 .
```

## Starting the Process
```
docker compose up -d
```

## Remote Control from a Host
Thanks to MQTT, you can remotely control movement and camera Pan-Tilt operations from a remote PC. When connecting a joystick to a remote Windows PC, you need to install:
- Python 3.10 or higher
- pygame

Then, execute:
```
python joypad_pygame.py
```
