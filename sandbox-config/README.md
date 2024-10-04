# Auto setup sandbox system

## File details

- `Vagrant`: Configuration file for auto download, install, setup and configure Windows 10 Virtual Machine on VirtualBox (Guest system for the Sandbox host).
- `run-vm.sh`: Power on the virtual machine in current working directory with the configuration file `Vagrant`.
- `reload-vm.sh`: Restart the virtual machine and update the newest config from configuration file without remove the VM. The `--provision` argument will make the VM executes init provision script from configuration file.
- `network-init.sh`: Set up the network for the virtual machine. The script will first check the configuration of the virtualbox for the allow to use all network address. If the configuration is not set, the script will set the configuration. Then the script will create a new host-only network adapter for the virtual machine with the name `vboxnet0` and the IP address `192.168.23.1` and the netmask `255.255.255.0` if the network adapter is not exist.
- `snapshot-vm.sh`: Create a snapshot for the `cybersec_windows_10` virtual machine with the name `snapshot1`.
- `cape-docker.sh`: Run the CAPEv2 docker container with the name `cape`.