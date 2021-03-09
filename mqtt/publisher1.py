#!/usr/bin/python3
from time import sleep
import paho.mqtt.client as mqtt

# MQTT Broker
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

def on_connect(mqttc, obj, flags, rc):
    print("rc:" + str(rc))

def on_publish(mqttc, obj, mid):
    print("publish: {0}".format(mid))

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

# MQTT Broker 接続
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)

mqttc.loop_start()

for i in range(1000):
    mqttc.publish("topic1", "test"+str(i))
    sleep(0.0001)
