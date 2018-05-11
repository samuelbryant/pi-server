#!/bin/bash

cd /home/sambryant/bin/github_projects/pi-server
ts=$(date)
echo "Starting LNS backup at $ts" >> logs/lns.log
python3 src/client/lns_backup.py
