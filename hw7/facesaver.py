#####
# Mosquitto Image Saver
#:wq <stephanie.mather@berkeley.edu>
#####

import paho.mqtt.client as mqtt
#import cv2
import numpy as np

from datetime import datetime

# Callback after connection
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("faces")

# Callback for new messages
def on_message(client, userdata, msg):
    print(msg.topic + " recieved data")

    # Name with the time received and save to file in S3 FUSE mount location.
    file = open("/mnt/hw7/" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "_face_new.png", "wb")
    file.write(msg.payload)

# Create client instance and connect
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mosquitto", 1883, 60)

client.loop_forever()
