#!/bin/bash
ts=$(date)
echo "This is a test script from /etc/cron.hourly/test_cron.sh." >> /home/sambryant/cron_test_README.txt
echo "This script was executed at $ts" >> /home/sambryant/cron_test_README.txt
