# Homework 9: Distributed Training and Neural Machine Translation

## Stephanie Mather

### Read up on OpenSeq2Seq
Nvidia [OpenSeq2Seq](https://github.com/NVIDIA/OpenSeq2Seq/) is a framework for sequence to sequence tasks such as Automatic Speech Recognition (ASR) and Natural Language Processing (NLP), written in Python and TensorFlow. Many of these tasks take a very long to train, hence the need to train on more than one machine.  In this week's lab, we'll be training a [Transformer-based Machine Translation network](https://nvidia.github.io/OpenSeq2Seq/html/machine-translation/transformer.html) on a small English to German WMT corpus.

### Get a pair of GPU VMs in Softlayer
Follow instructions in [Homework 6](https://github.com/MIDS-scaling-up/v2/tree/master/week06/hw) to get a pair of 2xP-100 or 2xV-100 VMs in Softlayer (remember that V-100s are about 3x faster than P-100s in mixed training). Please use the AC1_16X120X100 flavor for dual P-100 VMs or AC2_16X120X100 flavor for dual V-100 VMs. Call them, for instance, p100a and p100b.  If you are provisioning from our 2263543  image, docker and nvidia-docker will be already installed.  However, you will still need to log into the [Softlayer Portal](http://control.softlayer.com), find your instances under "devices" and "upgrade" them by adding a second 2 TB SAN drive to each VM, then format the 2TB disk and mount it to /data on each VM as described [here](https://github.com/MIDS-scaling-up/v2/blob/master/week03/hw/digits/README.md) under the "prepare the second disk" section.  Once you are finished with the setup, you will have a micro-cluster consisting of 2 nodes and four P-100 or V-100 GPUs total.

VM v100a
`ibmcloud sl vs create --datacenter=syd04 --hostname=v100a --domain=stephmather.com --image=2263543 --billing=hourly  --network 1000 --key=xxxxxx --flavor AC2_8X60X100 --san
`

VM v100b
`ibmcloud sl vs create --datacenter=syd04 --hostname=v100b --domain=stephmather.com --image=2263543 --billing=hourly  --network 1000 --key=xxxxxx --flavor AC2_8X60X100 --san
`

*I used the v100 image from HW6 and then upgraded the GPU to AC2_16X120X100 from the IBM Resize interface and added the 2TB hard disk. Alternatively I could have upgraded the GPUs when I created the VM with code such as:*
```
ibmcloud sl vs create --datacenter=syd04 --hostname=v100a --domain=stephmather.com --image=2263543 --billing=hourly  --network 1000 --key=xxxxxx --flavor AC2_16X120X100 --san
```
*By using the HW6 image the Nvidia, Docker and Tensorflow modules were already installed.*

![Upgraded Virtual Machine](/hw9/jpg/2_GPU_available_on_each.jpg)

Mounting the disk required following the previous instructions from week 1. vim wasn't installed so I modified /etc/fsta via cat: `cat > /etc/fstab` as follows:

```
LABEL=cloudimg-rootfs   /        ext4   defaults,relatime       0 0

# Added by Cloud Image build process
LABEL=cloudimg-bootfs   /boot   ext3    defaults,relatime    0 0
# CLOUD_IMG: This file was created/modified by the Cloud Image build process
# Mount the metadata disk for cloud-init, if present
LABEL=METADATA /var/lib/cloud/seed/config_drive vfat defaults,nofail 0 0
LABEL=SWAP-xvdb1        none    swap    sw,comment=cloudconfig  0       2
#mountdisk
/dev/xvdc /data                   ext4    defaults,noatime        0 0
```

### Create cloud containers for openseq2seq and distributed training

1. Create an account at https://ngc.nvidia.com/ *Complete in prior lab/hw*
1. Follow [these instructions](https://docs.nvidia.com/ngc/ngc-getting-started-guide/index.html#generating-api-key) to create an Nvidia Cloud docker registry API Key, unless you already have one. *COMPLETE*
1. Login into one of the VMs and use your API key to login into Nvidia Cloud docker registry *COMPLETE - followed the instructions to this in the nvidia docker environment: `docker login nvcr.io` Username: $oauthtoken, Password: xxxxx*
1. Pull the latest tensorflow image with python3: ```docker pull nvcr.io/nvidia/tensorflow:19.05-py3``` *COMPLETE*
1. Use the files on [docker directory](docker) to create an openseq2seq image *Clone docker files ```git clone https://github.com/MIDS-scaling-up/v2.git``` then create docker image ```cd v2/week09/hw/docker```. Then I built the container: ```docker build -t openseq2seq .```*
1. Copy the created docker image to the other VM (or repeat the same steps on the other VM) *I did the manual steps above on both VMs. First I pulled the git repo and then I built the container. It did not take very long and could be done at the same time so there was no time advantage to wait until the image was created on the first VM.*
1. Create containers on both VMs: ``` docker run --runtime=nvidia -d --name openseq2seq --net=host -e SSH_PORT=4444 -v /data:/data -p 6006:6006 openseq2seq ``` *COMPLETE*
1. On each VM, create an interactive bash sesion inside the container: ``` docker exec -ti openseq2seq bash ``` and run the following commands in the container shell: 
    1. Test mpi: ``` mpirun -n 2 -H <vm1 private ip address>,<vm2 private ip address> --allow-run-as-root hostname ``` *COMPLETE - showed that both v100a and v100b could be connected and seen*
    1. Pull data to be used in neural machine tranlsation training ([more info](https://nvidia.github.io/OpenSeq2Seq/html/machine-translation.html)):  *COMPLETE - This step took a long time,  approximately 1 hour*
    ``` 
    cd /opt/OpenSeq2Seq 
    scripts/get_en_de.sh /data/wmt16_de_en
    ```
    1. Copy configuration file to /data directory: ``` cp example_configs/text2text/en-de/transformer-base.py /data ``` *COMPLETE*
    1. Edit /data/transformer-base.py: replace ```[REPLACE THIS TO THE PATH WITH YOUR WMT DATA]``` with ```/data/wmt16_de_en/```,  in base_parms section replace ```"logdir": "nmt-small-en-de",``` with ```"logdir": "/data/en-de-transformer/",```  make "batch_size_per_gpu": 128, and the in eval_params section set "repeat": to True. *COMPLETE - see transformer-base.py*
    1. If you are using V-100 GPUs, modify the config file to use mixed precision per the instructions in the file and set  "batch_size_per_gpu": 256 (yes, you can fit twice as much data in memory if you are using 16-bit precision) *COMPLETE - see transformer-base.py for complete modifications to this file*
    1. Start training -- **on the first VM only:** ```nohup mpirun --allow-run-as-root -n 4 -H <vm1 private ip address>:2,<vm2 private ip address>:2 -bind-to none -map-by slot --mca btl_tcp_if_include eth0  -x NCCL_SOCKET_IFNAME=eth0 -x NCCL_DEBUG=INFO -x LD_LIBRARY_PATH  python run.py --config_file=/data/transformer-base.py --use_horovod=True --mode=train_eval & ``` *COMPLETE - before running I also checked that 2 GPUs were available: GPUs assigned to v100a and v100b are as expected, 4 GPUs available in total*
        ![GPUs assigned to v100a and v100b are as expected, 4 GPUs available in total](/hw9/jpg/2_GPU_available_on_each.jpg)
    1. Note that the above command starts 4 total tasks (-n 4), two on each node (-H <vm1 private ip address>:2,<vm2 private ip address>:2), asks the script to use horovod for communication, which in turn, uses NCCL, and then forces NCCL to use the internal nics on the VMs for communication (-x NCCL_SOCKET_IFNAME=eth0). Mpi is only used to set up the cluster.
    1. Monitor training progress: ``` tail -f nohup.out ``` *COMPLETE - I did have some troubleshooting to complete after aborting my first attempt when I realised I wanted to limit the number of maximum training steps. I had to delete the log files, model files and the nohup.out file before it would rerun.*
    1. Start tensorboard on the same machine where you started training, e.g. ```nohup tensorboard --logdir=/data/en-de-transformer``` You should be able to monitor your progress by putting http://public_ip_of_your_vm1:6006 ! *COMPLETE - See TensorFlow Screenshots for details in the questions below and in the [jpg](/hw9/jpg) file.*
    1. *You will run out of credits unless you kill them after 50,000 steps* (the config file will make the model run for 300,000 steps unless you change the max_steps parameter or kill training by hand) *I aborted my original training attempt (after only 500 steps) and restarted after reducing the max_steps parameter. This stoppped as expected at 50,000 steps. However I did have some delays both starting the training and cancelling the machines as I needed to download the models files. I ended up having the machines for longer, but still within my credit limits. Something I have no learned is that I can downgrade the GPU attached to the machine without effecting the hard disk. This allows you to reduce the cost of the machine when it is on standby considerably. An even better approach post training would be to mount an external location for the model files so they could be immediately downloaded.* 
    1. After your training is done, download your best model to your jetson tx2.  [Hint: it will be located in /data/en-de-transformer on the first VM]  Alternatively, you could always download a checkpoint from Nvidia [here](https://nvidia.github.io/OpenSeq2Seq/html/machine-translation.html) *Transferring the large model files was a new challenge for me as I could not use github to complete my task. With help from a friend I used sftp to download the file first from my VM to my jumpbox and then from my jumpbox to my Windows PC. Finally I completed the transfer from my Windows PC to my Jeston through direct sftp. This was my first time using secure file transfer protocol and it was quite simple and quick, although it required a few steps.*
 
### Create the tx2 container for openseq2seq 
Let us create a tx2 compatible container for OpenSeq2Seq.  We probably won't be able to use it for training, but it could be useful for inference.  Make sure that you have a local TF container in your TX2 that we created when we completed during [HW 5](https://github.com/MIDS-scaling-up/v2/tree/master/week05/hw). (We also have all TF containers posted [in the W251 docker hub](https://cloud.docker.com/u/w251/repository/docker/w251/tensorflow) ). Then, use [this Dockerfile](https://github.com/MIDS-scaling-up/v2/blob/master/week09/hw/docker/arm64/Dockerfile.dev-tx2-4.2_b158-py3) . We will need this container for our in-class lab.  Put your downloaded best trained model someplace onto the external hard drive of your jetson -- e.g. /data/en-de-transformer *COMPLETE*


### Submission

Please submit the nohup.out file along with screenshots of your Tensorboard indicating training progress (Blue score, eval loss) over time.  Also, answer the following (simple) questions:
*The [nohup.out](/hw9/nohup.out) is available in my github.*

* How long does it take to complete the training run? (hint: this session is on distributed training, so it *will* take a while)
*It took 6 hours for the first 12700  steps so I expected 50 000 to complete in the 24 hours. It actually completed in ~18 hours, faster than expected.*

* Do you think your model is fully trained? How can you tell?
*The model was not fully trained in only 50,000 steps, however it was starting to flatten out both the BLEU score and the evaluation loss so additional training would have diminshing returns. Based on the provided example, my model was performing better than the example model at 50000 steps (my BLEU score >0.365, example score <0.355 @ 50000 steps), but could have been improved up to ~0.380. Based on this, I expect my model would not have needed 300,000 steps to reach the same accuracy as the example model. The differences in training may be a result of different hardware. I completed my training on the V100 which is relatively new, the original model may have been completed on P100 GPUs. As found in hw6, this can result in differences.*

My Model BLEU curve
![My Model BLEU Score](/hw9/jpg/Eval_BLEU_Score.jpg)
Example Model BLEU curve
![Validation BLEU curve](/hw9/jpg/bleu2.jpg)

My validation loss:
![Validation loss curve](/hw9/jpg/eval_loss.jpg)
Example Validation loss
![Validation loss curve](/hw9/jpg/loss.jpg)

* Were you overfitting?
*From the evaluation loss graph above I was not overfitting the data, the loss has not yet reach a point where it is constant. However, I expect if I continued past ~100,000 steps it would flatten completely, signalling that overfitting was occuring and little to no accuracy gain would be available for evaluation data because the model is too fitted to the training data.*

* Were your GPUs fully utilized? *Yes, both GPUs on v100a and v100b were 100% utilised*

![v100a GPU Usage at 100%](/hw9/jpg/V100a_GPU_usage.jpg)
![v100b GPU Usage at 100%](/hw9/jpg/V100b_GPU_usage.jpg)

* Did you monitor network traffic (hint:  ```apt install nmon ```) ? Was network the bottleneck?
*I did monitor the network. I had to conduct `apt update` and then `apt instal nmon`. The network was not a bottleneck as it was set to 1GBps and ~ 250MBps was used the majority of the time.

![Network Monitoring Results](/hw9/jpg/Network_monitoring.jpg)

* Take a look at the plot of the learning rate and then check the config file.  Can you explain this setting?

![Learning Rates](/hw9/jpg/learning_rate.jpg)

*Taking a look at the above below the learning rate increases until the 8000th step and then gradually declines. This is confirmed by the configuration file setting the learning rate policy as transformer_policy with 8000 warm up steps.
`"lr_policy": transformer_policy,
  "lr_policy_params": {
    "learning_rate": 2.0,
    "warmup_steps": 8000,
    "d_model": d_model,
  },`
  Looking at the learning rate policy code (https://github.com/NVIDIA/OpenSeq2Seq/blob/master/open_seq2seq/optimizers/lr_policies.py) the transformer policy is based on the Adam Optimiser in Section 5.3 of [Attention is All You Need](https://arxiv.org/pdf/1706.03762.pdf). This increases the lr linearly for the warm-up steps and decreasing it thereafter proportionally to the inverse square root of the step number.

* How big was your training set (mb)? How many training lines did it contain?
*The English training set was 637MB and the German training set was 711MB. Both data sets contained 4562102 lines*

![Line Count Training set](/hw9/jpg/Word_cont_for_training_dataset.jpg)
*Including the processed files, the training data took 9260MB of memory in total*

![Total Memory of Training set](/hw9/jpg/total_memory_for_training_dataset.jpg)

* What are the files that a TF checkpoint is comprised of?
*The TF checkpoint contains the path of the model along with all the previous model paths. Each path contains the metadata, the index of the weights and the losses. The data file contains the tensors and their weights (i.e. the training variables) wheras the meta file contains the protocol buffer which saves the complete Tensorflow graph. The best model also has its own paths, metadata, index and weights.*
![Model Data Size](/hw9/jpg/model_size_data.jpg)

* How big is your resulting model checkpoint (mb)?
*From the above, the resulting best_model files are 4344MB in total. There 5 models in total in the best model file, each of which are ~871MB in total with the weights in the data file using most of that memory.*

* Remember the definition of a "step". How long did an average step take? 
*On average each step took 1.7 seconds. This can be seen in an extract from the nohup.out file*
![Time to complete step](/hw9/jpg/nohup_log.jpg)

* How does that correlate with the observed network utilization between nodes? *The if the network speed is reduced, the GPU utilisation drops below 100% as the network becomes the bottleneck and the time to complete a step increases. Thus the network speed is inverse to the step time.*

