#!/usr/bin/python3

import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)

mqttc.subscribe("topic1")

mqttc.loop_forever()
