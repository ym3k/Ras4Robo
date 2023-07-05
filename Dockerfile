FROM arm64v8/ros:humble
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-pigpio \
    wget \
    python3-paho-mqtt \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
COPY ydlidar/ydlidar*whl /tmp
RUN pip3 install `ls /tmp/ydlidar*whl` && rm /tmp/ydlidar*whl
