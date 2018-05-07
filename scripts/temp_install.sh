#!/bin/bash

# Moves scripts to places in the system so that they are "installed" in a way 
# that keeps track of all changes so they can be reverted later once a proper
# install method is devised


src="$1"
dst="$2"

if [[ "$#" -ne "2" ]]; then
  echo "Usage: $0 <src script> <dst>"
  exit 1
fi

if [[ ! -e "$src" ]]; then
  echo "Error: source doesnt exist"
  exit 1
fi

if [[ -e "$dst" ]]; then
  echo "Error: dest already exists"
  exit 1
fi

sudo cp "$src" "$dst"
parent=$(dirname "$0")
host=$(hostname)
echo "[$host]: cp '$src' '$dst'" >> "$parent/../install_list.txt"
