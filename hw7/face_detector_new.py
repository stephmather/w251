import sys
import os
import urllib

import numpy as np
import time

import cv2

import tensorflow.contrib.tensorrt as trt
import tensorflow as tf

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))



# Setting variables
FROZEN_GRAPH_NAME = 'data/frozen_inference_graph_face.pb'
IMAGE_PATH = 'data/warriors.jpg'

INPUT_NAME='image_tensor'
BOXES_NAME='detection_boxes'
CLASSES_NAME='detection_classes'
SCORES_NAME='detection_scores'
MASKS_NAME='detection_masks'
NUM_DETECTIONS_NAME='num_detections'
DETECTION_THRESHOLD=0.1

input_names = [INPUT_NAME]
output_names = [BOXES_NAME, CLASSES_NAME, SCORES_NAME, NUM_DETECTIONS_NAME]

# Load the frozen graph

output_dir=''
frozen_graph = tf.GraphDef()
with open(os.path.join(output_dir, FROZEN_GRAPH_NAME), 'rb') as f:
    frozen_graph.ParseFromString(f.read())

# Optimize the frozen graph using TensorRT

trt_graph = trt.create_inference_graph(
    input_graph_def=frozen_graph,
    outputs=output_names,
    max_batch_size=1,
    max_workspace_size_bytes=1 << 25,
    precision_mode='FP16',
    minimum_segment_size=50
)

# Create session and load graph

tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True

tf_sess = tf.Session(config=tf_config)

# use this if you want to try on the optimized TensorRT graph
# Note that this will take a while
# tf.import_graph_def(trt_graph, name='')

# use this if you want to try directly on the frozen TF graph
# this is much faster
tf.import_graph_def(frozen_graph, name='')

tf_input = tf_sess.graph.get_tensor_by_name(input_names[0] + ':0')
tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')
best_scores = []

# Create client and connect to MQTT broker
client = mqtt.Client()
client.on_connect = on_connect

client.connect("mosquitto", 1883, 60)


#Start video capture
cap = cv2.VideoCapture(1)
start = time.time()

while 1:
    # Detecting and processing pics
    ret, frame = cap.read()
    frame = cv2.resize(frame, (300, 300), interpolation = cv2.INTER_AREA)

    image_np = np.array(frame)
    scores, boxes, classes, num_detections = tf_sess.run([tf_scores, tf_boxes, tf_classes, tf_num_detections], feed_dict={
        tf_input: image_np[None, ...]
    })

    #print(scores)
    #print('boxes')
    #print(boxes)
    #print(classes)
    #print(num_detections)

    
    boxes = boxes[0]
    scores = scores[0]
    classes = classes[0]
    num_detections = num_detections[0]

    best_score_pos = np.argmax(scores)
    
    if scores[best_score_pos] >= DETECTION_THRESHOLD:
        best_scores.append(scores[best_score_pos])

        box = boxes[best_score_pos] * np.array([image_np.shape[0], image_np.shape[1], image_np.shape[0], image_np.shape[1]])

        frame = cv2.rectangle(frame, (int(box[1]), int(box[0])), (int(box[3]),int(box[2])), (255,0,0), 2) 

        frame = cv2.putText(frame, str(scores[best_score_pos]), (int(box[1]), int(box[0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        elapsed_time = time.time() - start
        #print('frame')
        #cv2.imshow("frame", frame)
        print("Score: " + str(sum(best_scores)/len(best_scores)))
        print("Frame Rate: " + str(len(best_scores)/elapsed_time))
    
    # Cop out face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        print(box)
        # Crop the face
        face_mat =  gray[int(box[0]):int(box[2]), int(box[1]):int(box[3])]
        #cv2.imshow("crop", face_mat)
        # Encode as PNG
        rc, png = cv2.imencode('.png', face_mat)
        msg = png.tobytes()
        # Publish to MQTT topic
        client.publish("faces", payload = msg, qos = 0, retain = False)
    
    # Loop breaking parameter
    k = cv2.waitKey(30) & 0xff
    if k == 27: 
        break

# Pause time
time.sleep(1) 
        
# Stop and clean-up
cap.release()
cv2.destiroyAllWindows()
