#!/bin/bash

PKG_DIR=/ydlidar-gs2/YDLidar-SDK
YDLIDAR_MODULE=dist/ydlidar-*.whl
cd $PKG_DIR/build
cmake ..
make
make install

cd $PKG_DIR
pip install .

python3 setup.py bdist_wheel && cp $PKG_DIR/$YDLIDAR_MODULE /ydlidar-gs2



