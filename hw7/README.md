# Homework 7 - Neural face detection pipeline

### Overview
The objective of this homework is simple: modify the processing pipeline that you implemented in 
[homework 3](https://github.com/MIDS-scaling-up/v2/blob/master/week03/hw/README.md) and replace the OpenCV-based face detector with 
a Deep Learning-based one. You could, for instance, rely on what you learned in 
[TensorRT lab 5](https://github.com/MIDS-scaling-up/v2/blob/master/week05/labs/lab_tensorrt.md) or 
[Digits lab 5](https://github.com/MIDS-scaling-up/v2/blob/master/week05/labs/lab_digits.md)

### Hints
* You have the freedom to choose the neural network that does the detection, but don't overthink it; this is a credit / no credit assignment that is not supposed to take a lot of time.
* There is no need to train the network in this assignment, just find and use a pre-trained model that is trained on a face dataset.
* Your neural detector should run on the Jetson.
* Just like the OpenCV detector, your neural detector needs to take a frame as input and return an array of rectangles for each face detected.
* Most neural object detectors operate on a frame of a given size, so you may need to resize the frame you get from your webcam to that resolution.
* Note that face detection is not the same as face recognition; you don't need to discriminate between different faces
* Here's a [sample notebook](hw07-hint.ipynb) that loads and uses [one face detector](https://github.com/yeephycho/tensorflow-face-detection)
* A more graceful solution would involve using a face detector from [TensorFlow's Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) -- [this network](http://download.tensorflow.org/models/object_detection/facessd_mobilenet_v2_quantized_320x320_open_image_v4.tar.gz), to be exact, but at the moment, simply loading it as we did in [TensorRT lab 5](https://github.com/MIDS-scaling-up/v2/blob/master/week05/labs/lab_tensorrt.md)  does not work due to [this bug](https://stackoverflow.com/questions/53563976/tensorflow-object-detection-api-valueerror-anchor-strides-must-be-a-list-wit)

### Questions
* Describe your solution in detail.  What neural network did you use? What dataset was it trained on? What accuracy does it achieve?

*The model used is the one offered in the hint notebook by yeephycho. [Avaiable from](https://github.com/yeephycho/tensorflow-face-detection). This is a  mobilenet SSD based face detector, powered by tensorflow object detection api. The model is trained on the WIDERFACE dataset, a face detection benchmark dataset, of which images are selected from the publicly available WIDER dataset.*

*The solution I have created is very similar to the architecture in Homework 3. In fact, the only changes made were the face_detector docker container used the mobilenet SSD based face detector and the face_saver container on the cloud was re-directed to a new bucket to save the faces. OpenCV was still used to save and process the images, just not to detect the faces.*

*OpenCV connects to the camera, the image is then resized to match the input size need for the face classifier. The classifier then predicts the presents of the face and Open CV is used to draw a rectangle over the captured face and display the accuracy of the prediction. I then converted the image to black and white and used a threshold of 0.1 accuracy before cropping out the faces and sending them to the [cloud](http://s3.au-syd.cloud-object-storage.appdomain.cloud/cos-smather-hw7).*

*The accuracy of face detection was highly varied, some frames were <0.1 and others >0.9. Average was somewhere around 0.5. Accuracy dropped for side images of the face and it also managed to pick up my face when it was partially obscured. It struggled when I had my glasses on and closed one eye however, suggesting an over reliance on the eyes to detect a face.*

* Does it achieve reasonable accuracy in your empirical tests? Would you use this solution to develop a robust, production-grade system?

*I tested a few different detection thresholds to boost the quality of the images sent to the cloud. The model definitiely has some frames with very low accuracy, even when facing front onto the camera. This means the algorithm is not accurate enough to pick up my face in every frame. Depending on the application, if a sizable amount of dropped frames is okay, this solution would be workable, but I would definitely not call it robust. Part of the issue is that it seems to get stuck on facial features such as an eye, instead of the whole face. I would try and increase the accuracy before using it in a production grade system.*

* What framerate does this method achieve on the Jetson? Where is the bottleneck?

*The framerate achieved was very fast when the display of the image was supressed. Starting at 0.2 and plateauing around 3 frames per second. The bottleneck appears to be in the network connection as it would speed up after a gap in sending images. The OpenCV detector was ~6 frames per second.*

* Which is a better quality detector: the OpenCV or yours?

*OpenCV is a bit better, it is more accurate and thus more robust for production.*
### To turn in:

Please provide answers to questions above, a copy of the code related to the neural face detector along with access to the location (object storage?) containing the detected face images. Note that this homework is NOT graded, credit / no credit only.

Code: see face_detection_new.py for neural face detector. Dockerfile for this docker container is also available. Notes contains the steps to create the entire pipeline.
Cloud storage: http://s3.au-syd.cloud-object-storage.appdomain.cloud/cos-smather-hw7
