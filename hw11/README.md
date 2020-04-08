# Homework 11 -- More fun with OpenAI Gym!

In this homework, I trained a Lunar Lander to land properly **using my Jetson TX2**. There is a video component to this file, so use a display or VNC.

There are two python scripts used for this process. The first file, `lunar_lander.py`, defines the Lunar Lander for OpenAI Gym. It also defines the keras model.

The second file, `run_lunar_lander.py`, instantiates the Lunar Lander environment and runs it.

### Change 1: No Change
The first time I trained the lunar lander I did not change any of the configuration.


### Results:
Viewing the videos the lunar lander moved erractically and was not very successful in making a landing. It had seemed to learn to move slower than the earlier landing attempts, but directionally it was still very inaccurate. At step  50000 the results were
```
loss: 137.6245
reward:  -4.480635533994297
total rewards  6.384399938092793
```

### Change 2: Adam to Adamax
The second time I ran the model I changed the optimizer to 'adamax'. [Adam](https://arxiv.org/abs/1412.6980) is an optimisation algorithm that can be used instead of the classical stochastic gradient descent. It utilises first order gradients to estimate the first and second moments to give an adaptive learning rate for different parameters. AdaMax is described in the same paper as a more stable version of Adam based on the infinity norm. The counteracts the instability of Adam for higher order moments and is good under conditions with sparse parameter updates. 

The code modification was:

```
def nnmodel(input_dim):
    model = Sequential()
    model.add(Dense(32, input_dim=input_dim, activation='relu'))
    model.add(Dense(16, activation='sigmoid'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adamax', metrics=['accuracy'])
    return model
```

Results:
Looking at the videos the lander was quicker to learn to stabilise itself in an upright position but it was still missing the flags. even in the final round of training (frame50000) it veered completely out of the window of the visualisation. 

```
loss:  202.9061
reward:  -0.4534947655698862
total rewards  -111.635338170586
Total successes are:  79
```



### Change 3: New CNN
The third change I made was to try and improve the neural network. By increasing complexity, I hoped to have a better accuracy and get the most succesful landings possible. I did not increase the number of layers, but I increased the size of the layers.

def nnmodel(input_dim):
    model = Sequential()
    model.add(Dense(512, input_dim=input_dim, activation='relu'))
    model.add(Dense(256, activation=relu))
    model.add(Dense(1, activation=linear))
    model.compile(loss='mean_squared_error', optimizer='adamax', metrics=['accuracy'])
    return model
    
    
Results:
Reviewing the videos again, increasing the neural network slowed the training process to start at 16s and dropping to <1 sec per batch. The original code was <1 sec per batch and the Adamax caused the training to speed up throughout the epoch(4s to <1 sec). At step  50000 the results were:

```
loss: 70.7458
reward:  0.261677597783722
total rewards  -152.9185408170793
Total successes are:  31
```
### Did you try any other changes that made things better or worse?
I changed the code to only save the frame output every 10000 steps. 

````
        if steps >= training_thr and steps %10000 == 0: #SM
            fname = "/tmp/videos/frame"+str(steps)+".mp4"
            skvideo.io.vwrite(fname, np.array(frames))
            del frames
            frames = []
        if steps >= training_thr and steps %1000 == 0: #SM
            #clear frames every 1000 steps, only save every 10000
            del frames
            frames = []
```
I also reduced the time the model to generate a random action candidate via lines 50-60 in `run_lunar_lander.py`:

```
        if modelTrained:
 #           maxr = -1000
 #           maxa = None
 #           for i in range(100):
 #               a1 = np.random.randint(-1000,1000)/1000
 #               a2 = np.random.randint(-1000,1000)/1000
 #               testa = [a1,a2]
 #               r_pred = model.predict(np.array(list(new_s)+list(testa)).reshape(1,len(list(new_s)+list(testa))))
 #               if r_pred > maxr:
 #                   maxr = r_pred
 #                   maxa = testa
 #           a = np.array(maxa)
            a_candidates = np.random.uniform(low=-1, high=1, size=(batch_size, 2))
            s_expanded = np.broadcast_to(new_s, (batch_size, 8))
            all_candidates = np.concatenate([s_expanded, a_candidates], axis=1)
            r_pred = model.predict(all_candidates)

            max_idx = np.argmax(r_pred)
            a = a_candidates[max_idx]
```

### Did they improve or degrade the model?
Both of these changes increased the speed at which the model trained but do not affect the accuracy.

### Based on what you observed, what conclusions can you draw about the different parameters and their values? 
Increasing the complexity of the training model through the CNN changes did not really improve the results, though it did seem to reduce the speed at which the model moved, i.e. it learnt to move slower not to crash, but struggled to learn to land efficiently. The changes to the learning rate through AdaMax was much more effective, it coused the model to converge faster by allowing the lr to vary. A next step to advance the model may be to start manipulating the reward system the lander gets. This could be done by manipluating the thresholds manually but higher performing solutions to the lunar_lander problem use actor-critic type algorithms. This is the curent reward (simple) system:
```
# Landing pad is always at coordinates (0,0). Coordinates are the first two numbers in state vector.
# Reward for moving from the top of the screen to landing pad and zero speed is about 100..140 points.
# If lander moves away from landing pad it loses reward back. Episode finishes if the lander crashes or
# comes to rest, receiving additional -100 or +100 points. Each leg ground contact is +10. Firing main
# engine is -0.3 points each frame. Solved is 200 points.
```



#### Enable http access to Cloud Object Storage

```
Here's how to enable http access to the S3 COS:
1) create a bucket & upload a file, remember the resiliency you pick and the location
2) Go to Buckets -> Access Policies -> Public Access
3) click the "Create access policy" button
4) Go to Endpoint (on the left menu) and select your resiliency to find your endpoint (mine was "Regional" because that's how I created my COS)
5) Your endpoint is the Public location plus your bucket name plus the file

Example: https://s3.eu-gb.cloud-object-storage.appdomain.cloud/brooklyn-artifacts/IBM_MULTICLOUD_MANAGER_3.1.2_KLUS.tar.gz

In this example, the bucket is "brooklyn-artifacts" and the single Region is eu-gb
```
