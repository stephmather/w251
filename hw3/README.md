# w251
MIDS w251
stephanie.mather@berkeley.edu

Repository that contais homework 3<https://github.com/MIDS-scaling-up/v2/tree/master/week03/hw> submissions for w251, January 2020.

Cloud output of live faces is available at http://s3.us-south.cloud-object-storage.appdomain.cloud/cloud-object-storage-smather-hw3-cos-standard-hq1

**notes.txt** conatians detatils of container configuration.

The following architechture was used
detector > mosquitto > forwarder > mosquitto > processor > objectstorage

## Jetson TX2
detector: A ubuntu conatiner on Jetson TX2 that uses openCV to recognise and extract faces from local usb camera feed. If a face is in frame, it is extracted and published via mqtt protocol to the forwarder using ***facedection.py*** 
mosquitto: The first mosquitto container is the mqtt broker on the Jetson TX2. It is an alpine conatiner running mosquitto.
forwarder: An alpine conatiner running paho-mqtt that subscribes to the faces published by the detector and forwards them onto the cloud virtual server using ***forwardtoCVSI.py***

## Cloud VSI
The could VSI is access trhough the w251 jumpbox and has two containers.
mosquitto: A alpine container running mosquitto that is the mqtt broker on the cloud VSI. It receives the message from the Jetson TX2 on port 1883.
processor: An ubuntu container that receives the faces via the mqtt broker and forwards them to the Cloud Object Storage using ***facesaver.py***

## Cloud Object Storage
A cloud object storage location was created under the users IBMCloud account to provide permenant storage for the face images. This could then be utilised fro processing at a later date. The cloud output of live faces is available at <http://s3.us-south.cloud-object-storage.appdomain.cloud/cloud-object-storage-smather-hw3-cos-standard-hq1>

