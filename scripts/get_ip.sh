#!/bin/bash
ifconfig | grep 'inet 192' | sed -E 's/.*inet ([0-9\.]*) .*/\1/g'
