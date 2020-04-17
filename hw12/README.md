# Homework: Part 1 - Installing GPFS FPO

## Overview

These instructions are a subset of the official instructions linked to from here: [IBM Spectrum Scale Resources - GPFS](https://www.ibm.com/support/knowledgecenter/en/STXKQY_5.0.1/com.ibm.spectrum.scale.v5r01.doc/bl1ins_manuallyinstallingonlinux_packages.htm).


We will install GPFS FPO with no replication (replication=1) and local write affinity.  This means that if you are on one of the nodes and are writing a file in GPFS, the file will end up on your local node unless your local node is out of space.

A. __Get three virtual servers provisioned__, 2 vCPUs, 4G RAM, CENTOS_7_64, __two local disks__ 25G and 100G each, in any datacenter. __Make sure__ you attach a keypair.  Pick intuitive names such as gpfs1, gpfs2, gpfs3.  Note their internal (10.x.x.x) ip addresses.
*Done, see example code:*
```
ibmcloud sl vs create --datacenter=syd01 --hostname=gpfs1 --domain=stephmather.com --billing=hourly --network 1000 --key=xxxxxx -c 2 -m 4096 --disk 25 --disk 100 -o CENTOS_7_64
```

B. __Set up each one of your nodes as follows:__

Add to /root/.bash\_profile the following line in the end:

    export PATH=$PATH:/usr/lpp/mmfs/bin

Make sure the nodes can talk to each other without a password.  When you created the VMs, you specified a keypair.  Copy it to /root/.ssh/id\_rsa (copy paste or scp works).  Set its permissions:

    chmod 600 /root/.ssh/id_rsa

Set up the hosts file (/etc/hosts) for your cluster by adding the __PRIVATE__ IP addresses you noted earlier and names for each node in the cluster.  __Also__ you should remove the entry containing the fully qualified node name for your headnode / gpfs1.sftlyr.ws (otherwise it will trip up some of the GPFS tools since it likely does not resolve). 
*Hosts file:*
```
cat > /etc/hosts
127.0.0.1 		localhost.localdomain localhost
10.138.179.16		gpfs1
10.138.179.26		gpfs2
10.138.179.30		gpfs3
```
Create a nodefile.  Edit /root/nodefile and add the names of your nodes.  This is a very simple example with just one quorum node:

    gpfs1:quorum:
    gpfs2::
    gpfs3::


C. __Install and configure GPFS FPO on each node:__
Install pre-requisites
```
#update the kernel & install some pre-reqs
yum install -y kernel-devel g++ gcc cpp kernel-headers gcc-c++ 
yum update
#reboot to use the latest kernel
reboot
#install more pre-reqs
yum install -y ksh perl libaio m4 net-tools
```

*Note, after reboot, the etc/hosts file must be modified again as it resets on restart: *
```
cat > /etc/hosts
127.0.0.1 		localhost.localdomain localhost
10.138.179.16		gpfs1
10.138.179.26		gpfs2
10.138.179.30		gpfs3
```
Then install S3 API client and GPFS with:

S3 Client
```
curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
yum install unzip
unzip awscli-bundle.zip
sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
aws configure
Access Key ID:
A1XGdUexhlIdyusn16Jh
Secret Access Key:
vImKKsEPfYQuzovEuPZjabeAViRhdQ9P85RQJEt1
aws --endpoint-url=https://s3-api.us-geo.objectstorage.softlayer.net  s3 cp s3://homework12/Spectrum_Scale_Advanced-5.0.3.2-x86_64-Linux-install Spectrum_Scale_Advanced-5.0.3.2-x86_64-Linux-install

```

GPFS installation (node that we are adding nodes using the node names, be sure to update the hosts file on each VM)
```
chmod +x Spectrum_Scale_Advanced-5.0.3.2-x86_64-Linux-install
./Spectrum_Scale_Advanced-5.0.3.2-x86_64-Linux-install --silent  (this command needs to be run on every node)
/usr/lpp/mmfs/5.0.3.2/installer/spectrumscale node add gpfs1  (this command needs to be run just gpfs1)
/usr/lpp/mmfs/5.0.3.2/installer/spectrumscale node add gpfs2  (this command needs to be run just gpfs1)
/usr/lpp/mmfs/5.0.3.2/installer/spectrumscale node add gpfs3  (this command needs to be run just gpfs1)

```
*Note: Orginially thie above steps would not execute and I realised I needed to create an ssh-key that did not require a password to unlock. I destroyed and rebuilt my cluster with a different ssh key. I then had no issues creating the cluster.*
D. __Create the cluster.  Do these steps only on one node (gpfs1 in my example).__
```
/usr/lpp/mmfs/5.0.3.2/installer/spectrumscale setup -s IP-OF-GPFS1  (this command needs to be run just gpfs1)
/usr/lpp/mmfs/5.0.3.2/installer/spectrumscale callhome disable   (this command needs to be run just gpfs1)
/usr/lpp/mmfs/5.0.3.2/installer/spectrumscale install  (this command needs to be run just gpfs1)
```
Now the cluster is installed, let's work the details.

Now, you must accept the license:

    mmchlicense server -N all (this command needs to be run just gpfs1)
    # (say yes)

Now, start GPFS:

    mmstartup -a (this command needs to be run just gpfs1)

All nodes should be up ("GPFS state" column shows "active"):
*Confirmed cluster state was active and nodes could communicate:*
    mmgetstate -a (this command needs to be run just gpfs1)
```
 Node number  Node name        GPFS state
-------------------------------------------
       1      gpfs1            active
       2      gpfs2            active
       3      gpfs3            active
```
Nodes may reflect "arbitrating" state briefly before "active".  If one or more nodes are down, you will need to go back and see what you might have missed. If some node shows a DOWN state, log into the node and run the command  mmstartup. The main GPFS log file is `/var/adm/ras/mmfs.log.latest`; look for errors there.

You could get more details on your cluster:

    mmlscluster (this command needs to be run just gpfs1)

Now we need to define our disks. Do this to print the paths and sizes of disks on your machine:

    fdisk -l (this command and the rest until the file creation command (touch aa) needs to be run just gpfs1)

*Noted the names of my 100G disks:*

```Disk /dev/xvdh: 67 MB, 67125248 bytes, 131104 sectors
Disk /dev/xvda: 26.8 GB, 26843545600 bytes, 52428800 sectors
Disk /dev/xvdc: 107.4 GB, 107374182400 bytes, 209715200 sectors
Disk /dev/xvdb: 2147 MB, 2147483648 bytes, 4194304 sectors
```

Now inspect the mount location of the root filesystem on your boxes:

    [root@gpfs1 ras]# mount | grep ' \/ '
    /dev/xvda2 on / type ext3 (rw,noatime)

Disk /dev/xvda (partition 2) is where my operating system is installed, so I'm going to leave it alone.  In my case, __xvdc__ is my 100 disk.  In your case, it could be /dev/xvdb, so __please be careful here__.  Assuming your second disk is `/dev/xvdc` then add these lines to `/root/diskfile.fpo`:

    %pool:
    pool=system
    allowWriteAffinity=yes
    writeAffinityDepth=1

    %nsd:
    device=/dev/xvdc
    servers=gpfs1
    usage=dataAndMetadata
    pool=system
    failureGroup=1

    %nsd:
    device=/dev/xvdc
    servers=gpfs2
    usage=dataAndMetadata
    pool=system
    failureGroup=2

    %nsd:
    device=/dev/xvdc
    servers=gpfs3
    usage=dataAndMetadata
    pool=system
    failureGroup=3

Now run:

    mmcrnsd -F /root/diskfile.fpo
    
You should see your disks now:

    mmlsnsd -m
```
[root@gpfs1 ~]# mmcrnsd -F /root/diskfile.fpo
mmcrnsd: Processing disk xvdc
mmcrnsd: Processing disk xvdc
mmcrnsd: Processing disk xvdc
mmcrnsd: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
  ```
Let’s create the file system.  We are using the replication factor 1 for the data:

    mmcrfs gpfsfpo -F /root/diskfile.fpo -A yes -Q no -r 1 -R 1
*Output:*
```
The following disks of gpfsfpo will be formatted on node gpfs3.stephmather.com:
    gpfs1nsd: size 102400 MB
    gpfs2nsd: size 102400 MB
    gpfs3nsd: size 102400 MB
Formatting file system ...
Disks up to size 895.99 GB can be added to storage pool system.
Creating Inode File
Creating Allocation Maps
Creating Log Files
Clearing Inode Allocation Map
Clearing Block Allocation Map
Formatting Allocation Map for storage pool system
Completed creation of file system /dev/gpfsfpo.
mmcrfs: Propagating the cluster configuration data to all affected nodes.  This is an asynchronous process
```

Let’s check that the file system is created:

    mmlsfs all
*Output*
```

File system attributes for /dev/gpfsfpo:
========================================
flag                value                    description
------------------- ------------------------ -----------------------------------
 -f                 8192                     Minimum fragment (subblock) size in bytes
 -i                 4096                     Inode size in bytes
 -I                 32768                    Indirect block size in bytes
 -m                 1                        Default number of metadata replicas
 -M                 2                        Maximum number of metadata replicas
 -r                 1                        Default number of data replicas
 -R                 1                        Maximum number of data replicas
 -j                 cluster                  Block allocation type
 -D                 nfs4                     File locking semantics in effect
 -k                 nfs4                     ACL semantics in effect
 -n                 32                       Estimated number of nodes that will mount file system
 -B                 4194304                  Block size
 -Q                 none                     Quotas accounting enabled
                    none                     Quotas enforced
                    none                     Default quotas enabled
 --perfileset-quota No                       Per-fileset quota enforcement
 --filesetdf        No                       Fileset df enabled?
 -V                 21.00 (5.0.3.0)          File system version
 --create-time      Mon Apr 13 00:16:44 2020 File system creation time
 -z                 No                       Is DMAPI enabled?
 -L                 33554432                 Logfile size
 -E                 Yes                      Exact mtime mount option
 -S                 relatime                 Suppress atime mount option
 -K                 whenpossible             Strict replica allocation option
 --fastea           Yes                      Fast external attributes enabled?
 --encryption       No                       Encryption enabled?
 --inode-limit      310272                   Maximum number of inodes
 --log-replicas     0                        Number of log replicas
 --is4KAligned      Yes                      is4KAligned?
 --rapid-repair     Yes                      rapidRepair enabled?
 --write-cache-threshold 0                   HAWC Threshold (max 65536)
 --subblocks-per-full-block 512              Number of subblocks per full block
 -P                 system                   Disk storage pools in file system
 --file-audit-log   No                       File Audit Logging enabled?
 --maintenance-mode No                       Maintenance Mode enabled?
 -d                 gpfs1nsd;gpfs2nsd;gpfs3nsd  Disks in file system
 -A                 yes                      Automatic mount option
 -o                 none                     Additional mount options
 -T                 /gpfs/gpfsfpo            Default mount point
 --mount-priority   0                        Mount priority
 ```
 
Mounting the distributed FS (be sure to pass -a so that the filesystem is mounted on all nodes):

    mmmount all -a

All done.  Now you should be able to go to the mounted FS:

    cd /gpfs/gpfsfpo

.. and see that there's 300 G there:

```
Filesystem      Size  Used Avail Use% Mounted on
gpfsfpo         300G  2.6G  298G   1% /gpfs/gpfsfpo
```

Make sure you can write, e.g.
*confirmed*
    touch aa

If the file was created, you are all set:

    ls -l /gpfs/gpfsfpo
    ssh gpfs2 'ls -l /gpfs/gpfsfpo'
    ssh gpfs3 'ls -l /gpfs/gpfsfpo'


# Part 2 - LazyNLP [Crawler library](https://github.com/MIDS-scaling-up/v2/blob/master/week12/hw/dataset.md)
# Homework: Part 2 LazyNLP

## Overview

[LazyNLP](https://github.com/chiphuyen/lazynlp) is a library / collection of scripts that allows you to crawl, clean up, and deduplicate webpages to create massive monolingual datasets. Using this library, you should be able to create datasets larger than the one used by OpenAI for GPT-2.


1. SSH into each node (gpfs1, gpfs2, gpfs3) and proceed to install the requisites for LazyNLP installation
```
  * yum install -y python3 python3-devel git
  * git clone https://github.com/chiphuyen/lazynlp.git
  * cd lazynlp
  * pip3 install -r requirements.txt
  * pip3 install .
 ``` 
2. Download the [The WikiText language modeling dataset](https://www.salesforce.com/products/einstein/ai-research/the-wikitext-dependency-language-modeling-dataset/) into the mounted distributed gpfs file system
  ```
  * cd /gpfs/gpfsfpo
  * wget https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-v1.zip
  * apt install unzip
  * unzip wikitext-103-v1.zip
  * rm -rf wikitext-103-v1.zip
  ```
3. Let's use LazyNLP to crawl a small (Gutenberg AUS) and medium (Gutenberg US) datasets.  Once you download the lists of urls below, you will need to modify the [crawler](https://github.com/MIDS-scaling-up/v2/blob/master/week12/hw/crawler.py) to point at these URL files.  Process the AUS file first. How long did it take? Now, kick off processing on the US file -- obviously, it will take a while, and by now, you should have a reasonable idea how long.
 ```
 * # Gutenberg US. About 50K books, about 14GB of text.
 * gdown https://drive.google.com/uc?id=1zIVaRaVqGP8VNBUT4eKAzW3gYWxNk728
 * # AUS Gutenberg. About 4k books, 1GB of text.
 * https://drive.google.com/uc?id=1C5aSisXMC3S3OXBFbnETLeK3UTUXEXrC
 * https://dumps.wikimedia.org/enwiktionary/20190301/enwiktionary-20190301-pages-articles-multistream.xml.bz2 (notice this is not a url.txt file but a text file)
  ```
4. Now, let's process a larger deduplicated collection of Reddit URLs. There are 163 separate URL files here, containing altogether 23M URLs. Your task is to download them all. Hint: you have three nodes and you can run many crawlers in parallel.
  ```
  * # The reddit dataset
  * pip install gdown
  * gdown https://drive.google.com/uc?id=1hRtA3zZ0K5UHKOQ0_8d0BIc_1VyxgY51
  * unzip reddit_urls.zip
  ```
5. If you run into weird "out of space" errors when clearly there's space, check your inode count:
```
mmdf gpfsfpo -F
# if you see the below
[root@gpfs3 gpfsfpo]# mmdf gpfsfpo -F
Inode Information
-----------------
Number of used inodes:          206848
Number of free inodes:               0
Number of allocated inodes:     206848
Maximum number of inodes:       206848

# to fix:
mmchfs gpfsfpo --inode-limit 15M
Set maxInodes for inode space 0 to 15728640
Fileset root changed.
[root@gpfs3 gpfsfpo]# mmdf gpfsfpo -F
Inode Information
-----------------
Number of used inodes:          206848
Number of free inodes:           53248
Number of allocated inodes:     260096
Maximum number of inodes:     15728640
[root@gpfs3 gpfsfpo]
# all better!
```

5. Feel free to suggest improvements and go after other data sets as needed (e.g. if your class project requires them)

### To Turn In
1. How much disk space is used after step 4?
2. Did you parallelize the crawlers in step 4? If so, how? 
3. Describe the steps to de-duplicate the web pages you crawled.
4. Submit the list of files you that your LazyNLP spiders crawled (ls -la).


Credit / No-credit only.  

#Please do not destroy the GPFS cluster as we will use it in class for labs.  


