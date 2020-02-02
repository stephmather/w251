#w251
Stephanie Mather

# Homework 4 Submission

#### 2. ConvnetJS MNIST demo
In this lab, we will look at the processing of the MNIST data set using ConvnetJS.  This demo uses this page: http://cs.stanford.edu/people/karpathy/convnetjs/demo/mnist.html
The MNIST data set consists of 28x28 black and white images of hand written digits and the goal is to correctly classify them.  Once you load the page, the network starts running and you can see the loss and predictions change in real time.  Try the following:
* Name all the layers in the network, make sure you understand what they do.

```
//create empty array to hold the layer information
layer_defs = [];
// input layer of size 24x24x1 (all volumes are 3D). This is a random sample of the 28x28x1 MNIST image
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
// a convolution layer with activation function relu. Applies a 5x5x1 kernel with stride 1 (stride is how many pixels across the function steps each time). 8 filters are applied to the kernel. Relu stands for rectified linear unit, and is a type of activation function. It is zero for all negative values.
layer_defs.push({type:'conv', sx:5, filters:8, stride:1, pad:2, activation:'relu'});
//Pooling layer to reduce the dimensionality of the data. This pools every 2x2 pixels into 1 pixel. The stride is 2.
layer_defs.push({type:'pool', sx:2, stride:2});
// a convolution layer with activation function relu. Applies a 5x5x1 filter with stride 1 (stride is how many pixels across the function steps each time).
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
//Pooling layer to reduce the dimensionality of the data. This pools every 3x3 pixels into 1 pixel. The stride is 3.
layer_defs.push({type:'pool', sx:3, stride:3});
// a softmax classifier predicting probabilities for ten classes: 0,1,2,3,4,5,6,7,8,9. softmax is a normalised exp. function
layer_defs.push({type:'softmax', num_classes:10});

#Build the model
net = new convnetjs.Net();
net.makeLayers(layer_defs);

#Run the model with l2 decay of 0.001 and model is updated every 20 samples
trainer = new convnetjs.SGDTrainer(net, {method:'adadelta', batch_size:20, l2_decay:0.001});
```

* Experiment with the number and size of filters in each layer.  Does it improve the accuracy?
The base code above takes ~ 5000 to reach .9 training accuracy and ~9000 samples to reach .9 validation accuracy. by 16000 samples the training accuracy is 0.95-0.99, validation is ~0.93.
Making both conv layers the same with 8 filters reduces training time (2sec forward time per sample). But the accuracy maxes out at training at ~0.92-0.95. The modified code is:
```
layer_defs = [];
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:5, filters:8, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:2, stride:2});
layer_defs.push({type:'conv', sx:5, filters:8, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:3, stride:3});
layer_defs.push({type:'softmax', num_classes:10});

net = new convnetjs.Net();
net.makeLayers(layer_defs);
```
Making both conv layers the same with 16 filters increases the forward time to 4-7sec per sample. 0.9 training accuracy was reach by ~5000 examples. by 15000 samples training accuracy is 0.95+ and validation 0.93+.
```
layer_defs = [];
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:2, stride:2});
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:3, stride:3});
layer_defs.push({type:'softmax', num_classes:10});

net = new convnetjs.Net();
net.makeLayers(layer_defs);
```
Doubling the size of the kernal to 10x10 decreasese the forward time to 2-3sec per sample. 0.9 training accuracy was reached by ~3000 examples but was unstable until 9000 samples. by 15000 samples training accuracy is 0.9+ and validation 0.93+. As expected, the resultant accuracy was lower than a kernel size of 5x5. This is because more detail is lost when a filter is used over a larger area.
```
layer_defs = [];
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:10, filters:8, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:2, stride:2});
layer_defs.push({type:'conv', sx:10, filters:16, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:3, stride:3});
layer_defs.push({type:'softmax', num_classes:10});

net = new convnetjs.Net();
net.makeLayers(layer_defs);
```
Changing the number and size of the filters did not improve the accuracy significantly from the original model.

* Remove the pooling layers.  Does it impact the accuracy?
Removing the pooling layers increases the backpropogation time through the network from 3 secs to 9 secs. The accuracy is not changed much in regards to number of samples trained when compared to the original algorithm. However, because the pooling reduced the computational time, the model without pooling is less computationally efficent.
```
layer_defs = [];
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:5, filters:8, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'softmax', num_classes:10});

net = new convnetjs.Net();
net.makeLayers(layer_defs);
```
* Add one more conv layer.  Does it help with accuracy?
Adding an additional convolution layer is similar to the original network. by 15000 samples training accuracy is 0.94-0.99 and validation is 0.9
```
layer_defs = [];
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:5, filters:8, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:2, stride:2});
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:3, stride:3});
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:3, stride:3});
layer_defs.push({type:'softmax', num_classes:10});

net = new convnetjs.Net();
net.makeLayers(layer_defs);
```
* Increase the batch size.  What impact does it have?
Batch size is the number of samples a neural network sees before the model is updated. The default batch size for ConvnetJS is 20. This was increased to 100. Generally you would expect a model to converge faster with a larger batch size. This was not evident in the MNIST cnn. The model converged slower and was less accurate for the same number of samples. It must be noted however that the number of epochs (the times the model aws updated) was different between the two. After 40000 samples the accuracy between the two models was similar.

*Accuracy convergence with batch size of 20*
![Batch Size 20 Image](batch20.jpeg)

*Accuracy convergence with batch size of 100*
![Batch Size 100 Image](batch100.jpeg)


* What is the best accuracy you can achieve? Are you over 99%? 99.5%?
I tried making the neural network wider as well as deeper, including a double convulution layer of two 3x3 layers instead of a single 5x5 layer. There was neglible increase in accuracy over the original model.

```
layer_defs = [];
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:3, filters:32, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'conv', sx:3, filters:32, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:2, stride:2});
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:3, stride:3});
layer_defs.push({type:'softmax', num_classes:10});

net = new convnetjs.Net();
net.makeLayers(layer_defs);

trainer = new convnetjs.SGDTrainer(net, {method:'adadelta', batch_size:20, l2_decay:0.001});
```


A more complex CNN based on the suggested architecture from https://machinelearningmastery.com/how-to-develop-a-convolutional-neural-network-from-scratch-for-mnist-handwritten-digit-classification/ was attempted. The training accuracy reached 0.9 at ~3000 samples but was very slow to train as the forward time per example was 25-30sec. Training accuracy reached 0.96-1 at 12000 samples. Validation accuracy moved between 0.92-0.96 by 15000 samples. This is still not dissimilar to the original model's accuracy.
```
layer_defs = [];
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:3, filters:32, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:2, stride:2});
layer_defs.push({type:'conv', sx:3, filters:64, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'conv', sx:3, filters:64, stride:1, pad:2, activation:'relu'});
layer_defs.push({type:'pool', sx:2, stride:2});
layer_defs.push({type:'fc', num_neurons:100, activation: 'relu'});
layer_defs.push({type:'softmax', num_classes:10});

net = new convnetjs.Net();
net.makeLayers(layer_defs);

trainer = new convnetjs.SGDTrainer(net, {method:'adadelta', batch_size:20, l2_decay:0.001});
```


#### 3. Build your own model in Keras
The [Conversation AI](https://conversationai.github.io/) team, a research initiative founded by [Jigsaw](https://jigsaw.google.com/) and Google (both a part of Alphabet) are working on tools to help improve online conversation. One area of focus is the study of negative online behaviors, like toxic comments (i.e. comments that are rude, disrespectful or otherwise likely to make someone leave a discussion).   
  
Kaggle are currently hosting their [second competition](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge#description) on this research. The challenge is to create a model that is capable of detecting different types of of toxicity like threats, obscenity, insults, and identity-based hate better than Perspective’s current models. The competitions use a dataset of comments from Wikipedia’s talk page edits. Improvements to the current model will hopefully help online discussion become more productive and respectful.

We shall be using this dataset to benchmark a number of ML models. 
*Disclaimer: the dataset used contains text that may be considered profane, vulgar, or offensive.*

##### a. Running on your Jetson
Your Jetson is quite powerful; let's start a keras / tensorflow - enabled jupyter notebook on it:
```
docker run --rm --privileged -p 8888:8888 -d  w251/tensorflow_hw04:dev-tx2-4.3_b132
# once you run this command, it will print the id of the container, e.g.
# root@dima-desktop:~/v2/backup/keras# docker run --rm --privileged -p 8888:8888 -d  w251/tensorflow_hw04:dev-tx2-4.3_b132 
7d783a4b0feb89fe91072c0d6934a000471fa101cf9e5b6c09b4b8d881291903

# Now, get the token from docker logs:
root@dima-desktop:~/v2/backup/keras# docker logs 7d783a4b0feb89fe91072c0d6934a000471fa101cf9e5b6c09b4b8d881291903
[I 16:11:29.070 NotebookApp] Writing notebook server cookie secret to /root/.local/share/jupyter/runtime/notebook_cookie_secret
[I 16:11:30.208 NotebookApp] Serving notebooks from local directory: /notebooks
[I 16:11:30.208 NotebookApp] The Jupyter Notebook is running at:
[I 16:11:30.208 NotebookApp] http://7d783a4b0feb:8888/?token=0cebf472b557f2e871de6be4e0717ff35cdd30b013b0d7e5
[I 16:11:30.209 NotebookApp]  or http://127.0.0.1:8888/?token=0cebf472b557f2e871de6be4e0717ff35cdd30b013b0d7e5
[I 16:11:30.209 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation)
```
Now, point your browser to http://yourjetsonip:8888?token=yourtoken

##### b. Running in the Cloud
Set up a CPU based VM to run your models. We shall use sparse matrices which are better suited to CPU than GPU. 
I set the VM up like below, you may need to change the `datacenter` and `domain`.
```
ibmcloud sl vs create --datacenter=lon06 --hostname=hw04cpu --domain=darragh.com --os=UBUNTU_16_64 --flavor C1_8X8X100 --billing=hourly --san --disk=100 --disk=2000 --network 1000  --key=1418191
```
As before check the VM is created with `ibmcloud sl vs list`  
Login like `ssh -i /home/darragh/.ssh/id_rsa 158.176.93.70 -l root` or `ssh root@158.176.93.70`. You may need to wait a couple of minutes before logging in for the VM to br created. 

Once logged into the VM as `root` user, **Install docker**:
```
# Validate these at https://docs.docker.com/install/linux/docker-ce/ubuntu/
apt-get update
apt install apt-transport-https ca-certificates 
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic test" 
apt update 
apt install docker-ce
# Validated 09/14/19 - Darragh
# Test if docker hello world is working
docker run hello-world
```

Now we pull the image and start our jupyter notebook. 
```
docker run --rm -it -p 8888:8888 w251/tensorflow_hw04:latest
```

You will have an output of the location of the book running line below
```
[I 11:47:41.840 NotebookApp] The Jupyter Notebook is running at:
[I 11:47:41.841 NotebookApp] http://(5ebf32ea4e17 or 127.0.0.1):8888/?token=ffbb6d6b3a9b2e24fb8e0cc7eb8eb0657e1f58fa5595c5d4
```
Replace the domain name of the URL with your servers, public IP. For example for the above output I would go to URL. 
```
http://158.176.93.70:8888/?token=ffbb6d6b3a9b2e24fb8e0cc7eb8eb0657e1f58fa5595c5d4
```
Now open the notebook and run. And fill in the codes blocks marked for filling in and monitor your AUC. 
For the Logistic regression model you should be getting circa `0.88` AUC and `0.93` or more for the MLP. 

#### Submission:
Please submit answers to #2, and a html download of your completed Jupyter notebook. A link to a github repo is a great way to submit.
 

PLEASE CANCEL YOUR VM ONCE YOU ARE DONE!!!

## Note on cloud usage
![Soflayer](../../softlayer.png?raw=true "Title")
