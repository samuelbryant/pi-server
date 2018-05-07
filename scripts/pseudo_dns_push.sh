#!/bin/bash
## Pushs the external IP address of the source to the UChicago linux computers
## so that it can be re-obtained in case it changes.
## This is sort of a fake DNS table with one entry.

## This version of the script can be run as a cron job.

USERNAME="sambryant"
UCHI_SERVER="linux.cs.uchicago.edu"
EXT_IP_FILE="SJB_PI_IP"
LOCAL_IP_FILE="SJB_PI_IP_LOCAL"

# Get the local and external IP addresses.
ip=$(ifconfig | grep 'inet 192' | sed -E 's/.*inet ([0-9\.]*) .*/\1/g')
ext_ip=$(curl ipinfo.io/ip)

if [[ "$?" -ne "0" ]]; then
  exit 1
fi

# Publish them to UChicago's server.
echo "$ip" | ssh -o "StrictHostKeyChecking no" "${USERNAME}@${UCHI_SERVER}" 'cat > '"$LOCAL_IP_FILE"
echo "$ext_ip" | ssh -o "StrictHostKeyChecking no" "${USERNAME}@${UCHI_SERVER}" 'cat > '"$EXT_IP_FILE"

exit 0
