FROM ubuntu:22.04
RUN apt-get update && apt-get install --no-install-recommends -y \
    make g++ \
    cmake pkg-config \
    python3 swig \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
