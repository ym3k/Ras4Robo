FROM arm64v8/ros:humble
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-pigpio \
    && rm -rf /var/lib/apt/lists/*
