###
# Face Detector with MQTT
# <stephanie.mather@berkeley.edu>
###


import paho.mqtt.client as mqtt
import cv2

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Create client and connect to MQTT broker
client = mqtt.Client()
client.on_connect = on_connect

client.connect("mosquitto", 1883, 60)

# Use pre-trained classifier
face_cascade = cv2.CascadeClassifier('/mnt/opencv/haarcascade_frontalface_default.xml')

# 1 should correspond to /dev/video1 , your USB camera. The 0 is reserved for the TX2 onboard camera
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # We don't use the color information, so might as well save space
    #print frame.shape
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform face detection
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    #print faces when detection occurs
    print(faces)

    for(x,y,w,h) in faces:
        # Crop the face
        face_mat =  gray[y:y+h, x:x+h]
        # Encode as PNG
        rc, png = cv2.imencode('.png', face_mat)
        msg = png.tobytes()
        # Publish to MQTT topic faces
        client.publish("faces", payload = msg, qos = 0, retain = False)
