#!/bin/bash

IP_ADDRESS="192.168.23.1"

if VBoxManage list hostonlyifs | grep -q "Name:            vboxnet0"; then
    echo "vboxnet0 network exist. Removing..."
    VBoxManage hostonlyif remove vboxnet0
fi

echo "Creating vboxnet0 network..."
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet0 --ip "$IP_ADDRESS" --netmask 255.255.255.0

echo "Created vboxnet0 with IP: $IP_ADDRESS."

