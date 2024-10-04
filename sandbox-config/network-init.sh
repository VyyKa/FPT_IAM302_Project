#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root or use sudo."
    exit 1
fi

# Check if string "* 0.0.0.0/0 ::/0" in file /etc/vbox/networks.txt
if grep -q "* 0.0.0.0/0 ::/0" /etc/vbox/networks.txt; then
    echo "Networks are already configured."
else
    echo "Configuring networks..."
    echo "* 0.0.0.0/0 ::/0" >> /etc/vbox/networks.txt
fi

IP_ADDRESS="192.168.23.1"

if VBoxManage list hostonlyifs | grep -q "Name:            vboxnet0"; then
    echo "vboxnet0 network exist. Removing..."
    VBoxManage hostonlyif remove vboxnet0
fi

echo "Creating vboxnet0 network..."
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet0 --ip "$IP_ADDRESS" --netmask 255.255.255.0

echo "Created vboxnet0 with IP: $IP_ADDRESS."

