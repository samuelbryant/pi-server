#!/bin/bash
# Library settings
## Machine install location
#DEFAULT_LIB_LOCATION="/usr/local/lib/python3.6/dist-packages"
## Local install location (use until ready for prod)

APP_LIB_NAME="piserver"

#DEFAULT_LIB_LOCATION="/usr/local/lib/python3.6/dist-packages"
DEFAULT_LIB_LOCATION="$HOME/.local/lib/python3.6/site-packages"
DEFAULT_FRONTEND_LOCATION="/usr/local/bin"
#DEFAULT_CONFIG_LOCATION="/usr/local/etc"
DEFAULT_CONFIG_LOCATION="$HOME/.config/"


LOCAL_FRONTEND_LOCATION="./bin"
LOCAL_LIB_LOCATION="./src"
LOCAL_CONFIG_LOCATION="./config"

# Make sure we are not running as sudo user:
if [ "$EUID" -eq 0 ]; then
  echo "Error: script cannot be run as root (dont use sudo)"
  exit 1
fi

# Check that python3.6 is installed
python3.6 --version 2>/dev/null 1>/dev/null
if [ "$?" -ne "0" ]; then
  echo "Error: python3.6 not found. Make sure its installed first"
  exit 2
fi


# Check that install directory is in the python library path:
python3.6 -c "import sys; sys.exit('$DEFAULT_LIB_LOCATION' not in sys.path)"
if [ "$?" -ne "0" ]; then
  echo "Error: Install directory ('$DEFAULT_LIB_LOCATION') was not found in python path (sys.path)"
fi

# Make the directories that are not specific to this app.
mkdir -p "$DEFAULT_LIB_LOCATION"
mkdir -p "$DEFAULT_CONFIG_LOCATION"

# App-specific directories
target_pylib_name="$DEFAULT_LIB_LOCATION/$APP_LIB_NAME"
target_config_name="$DEFAULT_CONFIG_LOCATION/$APP_LIB_NAME"

## Check that no installation already exists:
if [[ -e "$target_pylib_name" ]]; then
  echo "Error: target app library already exists ('$target_pylib_name')" >> /dev/stderr
  exit 1
elif [[ -e "$target_config_name" ]]; then
  echo "Error: target app config dir already exists ('$target_config_name')" >> /dev/stderr
  exit 1
fi

# Now we make the actual installation
set -e
mkdir -p "$target_config_name"
cp -rf "$LOCAL_LIB_LOCATION/$APP_LIB_NAME" "$target_pylib_name"
cp -rf "$LOCAL_CONFIG_LOCATION/*" "$target_config_name/"
sudo cp -rf "$LOCAL_FRONTEND_LOCATION/*" "$DEFAULT_FRONTEND_LOCATION/"

echo "Installation was a success!"
