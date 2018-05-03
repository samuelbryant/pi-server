This repo hosts all of the things I need to make my raspberry pi into a file backup server.
This documents describes the general outline of how I will store my data locally and remotely as well as how I will synchronize between the two.


## Drives
There are FIVE drives that will be important here:

  home = [Laptop] my laptops native storage in my home folder
  sda1 = [Laptop] the 90 GB flash drive partition attached to my laptop
  sda2 = [Laptop] the 30 GB encrypted partitoin on flash drive attached to laptop
  rpi1 = [Server] the 250 GB SSD attached to my raspberry pi
  rpi2 = [Server] the 2 TB hard drive attached to my raspberry pi

## Data types
I basically have three types of data.

1. SNS Small non-sensitive data - this includes program code, scripts, writing exericises, music, class work, etc. 
2. LNS Large non-sensitive data - this includes photos, TV shows, movies, music, Textbooks
3. SEN Sensitive data - includes tax information and anything else secretive

## Asumptions
Going forward I will make the following assumptions:

### Data privacy:
1. LNS and SNS data should not be easily accessible by others, but someone with the know-how can see it if they really wanted. Basically, I don't want my peers to stumble across this. This means we need basic protection against NON-malicious actors.
2. SEN data should not be accessible to anyone but me. Even an expert should not be able to obtain this data. i.e. encryption.

### Data volatility:
1. SNS data will change often. Not only will files come and go, but files will also change a lot.
2. LNS data will often be written once and never modified. This is true for Textbooks, Movies, Photos, Music. This means that flash drive storage is accetable here.
3. SEN data is completely unpredictable. Since SEN is a catch-all that doesn't distinguish between kinds of data, we can't make any assumptions here. Also it is unclear what factor encryption has on volativity.

### Data size:
1. SNS data should total under 30 GB. Ideally under 15 GB.
2. LNS data may be large. For now, we assume under 80 GB, but that might have to change.
3. SEN data is somewhere in the middle. Assume it totals under 30 GB.

### Write direction: 
(this assumption may only be temporary.)
1. SNS, LNS, and SEN are all changed LOCALLY and backups are kept on the SERVER. The opposite flow never happens.

## Basic Proposal
Client-Server full file redundancy with secondary backups. I'll explain what this means:

1. SNS, LNS, and SEN all live *somewhere* locally.
2. SNS, LNS, and SEN also have an identical backup on the server.
3. LNS has one or more additional backups on server taken periodically.
4. SNS has one or more additional backups on the server taken periodically.

### Details
On the local side:
1. SNS lives on `home`
2. LNS lives on `sda1`
3. SEN lives on `sda2`

On the server side:
1. a nightly (?) backup of SNS exists on `rpi1`. Backup is completed via `rsync` run using `cron`
2. a nightly (?) backup of LNS exists on `rpi1`. Backup is completed via `rsync` run using `cron`
3. manual backups of SEN exist on `rpi1`. Backup method is TBD
4. There is an additional cron job that runs on the server that copies the entire backup to `rpi2`
