####
# MQTT Forwarder
# <stephanie.mather@berkeley.edu>
####

import paho.mqtt.client as mqtt

#Topic to forward
topic_from = "faces"
topic_to = "faces"
local_host = "mosquitto"
cloud_host = "130.198.90.186"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("LOCAL Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic_from)

def on_cloud_connect(client, userdata, flags, rc):
    print("CLOUD Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    print(msg.topic + "received")

    # Forward data as-is
    cloud_client.publish(topic_to, payload = msg.payload, qos = 0, retain = False)


# Create client and connect locally
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(local_host, 1883, 60)

# Create client and connect to cloud instance
cloud_client = mqtt.Client()
cloud_client.on_connect = on_cloud_connect

cloud_client.connect(cloud_host, 1883, 60)



while True:

    client.loop()
    cloud_client.loop()
