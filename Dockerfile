FROM arm64v8/ros:humble
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-pigpio \
    wget \
    python3-paho-mqtt \
    && rm -rf /var/lib/apt/lists/*
