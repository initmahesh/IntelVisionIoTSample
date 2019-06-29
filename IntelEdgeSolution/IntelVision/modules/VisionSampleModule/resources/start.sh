#!/bin/bash
if [ ! -d "/etc/udev/rules.d" ]; then
    mkdir -p "/etc/udev/rules.d"
fi
/opt/intel/computer_vision_sdk/install_dependencies/install_NCS_udev_rules.sh
python3 -u cleanroom_cpu_demo.py
