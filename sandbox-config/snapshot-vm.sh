#!/bin/bash

# Define variables
name="snapshot1"
name_vm="cybersec_windows_10"

# Take a snapshot of the VM
VBoxManage snapshot "$name_vm" take "$name" --pause

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Snapshot '$name' taken successfully for VM '$name_vm'."
else
    echo "Failed to take snapshot '$name' for VM '$name_vm'."
fi

