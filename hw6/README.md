# Homework 6

**Note this is a graded homework.**
1. Read the Google Cloud Product Overview on the [TPUs](https://cloud.google.com/tpu/)  
2. Read the primer on [Bert](https://github.com/google-research/bert)  
3. Follow the below steps to run BERT in pytorch on the Jigsaw Toxicity classification dataset.  
  
### Instructions 
You will be training BERT in a jupyter notebook. Please read the below points before starting.    
* The book is set with 10K rows training and 5K rows validation - so you can test it fast in your initial development. For your final run, we would like you to train on at least 1M rows; and validate on at least 500K rows.  
* Please run it on a V100 VM and a P100 VM and report run times on training 1M rows on both. (Note, V100 will be faster, so maybe good to start there).   
* You have 8 sections found in the jupyter notebook to complete the training of BERT and answer some questions. The first 5 seem challenging - but there is a script linked in the book which should make help a lot - should be just copy and pasting the correct code chunks.   
* Your submission should be your completed notebook (either from the P100 or V100). You can submit either through a HTML or link to a private GitHub repo.   
* Please let your instructors know if it is taking an excessive amount of time. The scripts do run long on 1M rows ~ a number of hours on the both types of VM's, but the development should not take an excessive amount of time.  
* The final section in the book shows a number of tasks, you need only complete 1 of them.   
* **For turning in your work**, please send instructors the link your repo containing your completed notebooks and information on P100 and V100 runtimes etc., alternatively, mail instructors the notebooks in html format along with runtimes. 
  
  
### Start your VMs and notebook as below.  
    
Start your `ibmcloud` VM. I ran like below - note this is a P100. You will need to replace the key.   
If you use `slcli`, no need to add `--san`.  
```
ibmcloud sl vs create --datacenter=lon06 --hostname=p100a --domain=dima.com --image=2263543 --billing=hourly  --network 1000 --key=1418191 --flavor AC1_8X60X100 --san
```

```
ibmcloud sl vs create --datacenter=syd04 --hostname=p100a --domain=stephmather.com --image=2263543 --billing=hourly  --network 1000 --key=xxxxxx --flavor AC1_8X60X100 --san


For your v100, enter,
```
ibmcloud sl vs create --datacenter=lon04 --hostname=v100a --domain=dima.com --image=2263543 --billing=hourly  --network 1000 --key=1418191 --flavor AC2_8X60X100 --san
```
ibmcloud sl vs create --datacenter=syd04 --hostname=v100a --domain=stephmather.com --image=2263543 --billing=hourly  --network 1000 --key=xxxxxx --flavor AC2_8X60X100 --san


**Created Machines:

`ssh` into your machine and run the below. 
```
nvidia-docker run --rm --name hw06 -p 8888:8888 -d w251/hw06:x86-64
```
   
The above will output a `containerid` on completion, like `959f320ffed2cce68ff19d171dcd959e33ebca30a818501677978957867d96fe`
With this run the below to get your URL. 
```
docker logs <containerid>
```
  
After you run this you will get an output like below. Go into your book, replacing the public IP in the brackets. For example for the below you can go to url   `http://158.176.131.11:8888/?token=c5d34fc988f452c4105c77a56924fe392d52991dde48478e`
```
	root@p100:~# docker run --rm --runtime=nvidia -it -p 8888:8888 -v /root:/root w251/pytorch_gpu_hw06
	[I 18:46:45.371 NotebookApp] Serving notebooks from local directory: /workspace
	[I 18:46:45.371 NotebookApp] The Jupyter Notebook is running at:
	[I 18:46:45.371 NotebookApp] http://(bef46d014d15 or 127.0.0.1):8888/?token=c5d34fc988f452c4105c77a56924fe392d52991dde48478e
	[I 18:46:45.371 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).

```

## Runtimes

The v100 was significantly faster than the p100 for training the model, but the p100 had marginally faster performance for the tokenizer. The slower performance for the v100 for the tokenizer may be a function of time of day the notebook was run and the latency on the network. There is significant distance from my current location to the nearest data centre in Sydney Australia. The increased speed and core number from the v100 become significant for the higher level tasks, taking less than half the runtime to complete 2_epochs.

It is interesting to note that no increase in accuracy came from running the BERT model through 2 epochs instead of 1, instead it actually fell slightly for the v100. But, the change in accuracy between the 1 and 2 epoch models is too small to be considered significant. The accuracy between the v100 and p100 models is almost identical, with the p100 performing slighlty better. This reflects the similarities in hardware. v100 is a newer, faster model of the p100 with the addition of 640 Tensor Cores. This allows the v100 to process the model faster than you would expect from the additional hardware specs (3584 CUDA cores versus 5120 & 1.126GHz versus 1.53 GHz).


The tokenizer:
v100:
```
loaded 1500000 records
33724
CPU times: user 33min 47s, sys: 9.64 s, total: 33min 56s
Wall time: 33min 47s
```

p100
```
loaded 1500000 records
33724
CPU times: user 25min 27s, sys: 7.12 s, total: 25min 34s
Wall time: 25min 26s
```

2_epoch Training times:
v100:
```
CPU times: user 3h 10min 35s, sys: 49min 2s, total: 3h 59min 38s
Wall time: 3h 59min 31s
```

p100
```
CPU times: user 7h 35min 52s, sys: 4h 32min 18s, total: 12h 8min 11s
Wall time: 12h 7min 42s
```


Validation of the Model:
v100:
```
CPU times: user 14min 8s, sys: 1min 49s, total: 15min 57s
Wall time: 15min 53s
```

p100
```
CPU times: user 37min 56s, sys: 22min 45s, total: 1h 42s
Wall time: 1h 36s
```

AUC Score (1 epoch)
v100:
```
AUC score : 0.96990
```

p100
```
AUC score : 0.97000
```

AUC Score (2 epoch)
v100:
```
AUC score : 0.96968
```

p100
```
AUC score : 0.97000
```
