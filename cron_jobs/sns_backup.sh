#!/bin/bash

cd /home/sambryant/bin/github_projects/pi-server
ts=$(date)
echo "Starting SNS backup at $ts" >> /logs/sns.log
python3 src/client/sns_backup.py
