#!/bin/bash

ts=$(date)
echo "this systemd unit was set up at 7:00pm may 8" > "/home/sambryant/systemd_README.txt"
echo "This systemd unit was excuted at $ts" >> "/home/sambryant/systemd_README.txt"
