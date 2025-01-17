#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root or use sudo."
    exit 1
fi

BASE_DIR=$(pwd)

VAGRANTFILE_URL="https://gist.githubusercontent.com/nquangit/83633b69f28757217b1222d112b1a4c3/raw/d9c9974b6eb985e8095387f472790cea5d02bba4/Vagrant"

# VM variables
VM_NAME="cybersec_windows_10"
VM_SNAPSHOT="snapshot1"
VM_CPUS=2
VM_RAM=4096
VM_NETWORK="vboxnet0"
VM_ADAPTER="Ethernet 2"
VM_IP="192.168.23.133"
VM_SUBNET="255.255.255.0"
VM_GW="192.168.23.1"
VM_DNS="192.168.23.1"

# Virtualbox host-only network variables - DON'T CHANGE
HOST_ONLY_NETWORK="$VM_NETWORK" # vboxnet0
HOST_ONLY_IP="$VM_GW" # 192.168.23.1
HOST_ONLY_NETMASK="$VM_SUBNET" # 255.255.255.0

# Get the current user
CURRENT_USER=${SUDO_USER:-$(whoami)}

# List of dependencies
dependencies=(
    "virtualbox"
    "curl"
    "git"
    "wget"
    "vim"
    "build-essential"
    "vagrant"
    "ovmf"
    "golang"
    "net-tools"
)

# Colors for formatting
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a package is installed
is_installed() {
    dpkg -l "$1" &> /dev/null
}

# Pretty print with status icons
pretty_print() {
    echo -e "${BLUE}Checking dependency:${NC} $1"
}

success_message() {
    echo -e "${GREEN}✔ $1 is already installed.${NC}"
}

install_message() {
    echo -e "${YELLOW}➜ Installing $1...${NC}"
}

error_message() {
    echo -e "${RED}✘ Failed to install $1.${NC}"
}

# Check if the system has internet connection
check_internet() {
    ping_output=$(ping -c 1 google.com 2>&1)
    # Check if the ping Temporary failure in name resolution
    if [[ $ping_output == *"Temporary failure in name resolution"* ]]; then
        # Notify DNS issue
        echo -e "${RED}✘ DNS issue detected.${NC}"
        # Read the user input to automatically fix the DNS issue
        read -p "Do you want to fix the DNS issue automatically? (y/n): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Fix the DNS issue automatically
            echo -e "${BLUE}Fixing the DNS issue...${NC}"
            echo "nameserver 8.8.8.8" > /etc/resolv.conf
            echo "nameserver 8.8.4.4" >> /etc/resolv.conf
            echo -e "${GREEN}✔ DNS issue is fixed.${NC}"
            # Recheck the internet connection
            check_internet
        else
            # Notify the user to fix the DNS issue manually
            echo -e "${RED}✘ Please fix the DNS issue manually.${NC}"
            exit 1
        fi
    else
        # Check if the ping is successful
        if [[ $ping_output == *"1 packets transmitted, 1 received"* ]]; then
            # Notify the user that the internet connection is available
            echo -e "${GREEN}✔ Internet connection is available.${NC}"
        else
            # Notify the user that the internet connection is not available
            echo -e "${RED}✘ Internet connection is not available.${NC}"
            exit 1
        fi
    fi
}

# Function to check if apt package manager is available
check_apt() {
    echo -e "${BLUE}Checking for apt package manager...${NC}"
    
    if command -v apt-get > /dev/null; then
        echo -e "${GREEN}✔ apt package manager is available.${NC}"
    else
        echo -e "${RED}✘ apt package manager is not available on this system.${NC}"
        echo -e "${RED}This script requires a system that uses apt (e.g., Ubuntu, Debian).${NC}"
        exit 1
    fi
}

# Function to check for hardware virtualization support
check_virtualization() {
    echo -e "${BLUE}Checking hardware virtualization support...${NC}"
    
    if egrep -q 'vmx|svm' /proc/cpuinfo; then
        echo -e "${GREEN}✔ Hardware virtualization is supported.${NC}"
    else
        echo -e "${RED}✘ Hardware virtualization is not supported on this system.${NC}"
        echo -e "${RED}Please enable virtualization in your BIOS settings or check your hardware compatibility.${NC}"
        exit 1
    fi
}

install_dependencies() {
    echo -e "${BLUE}Updating package list...${NC}"
    sudo apt-get update > /dev/null 2>&1
    
    # Install missing dependencies
    for package in "${dependencies[@]}"; do
        pretty_print "$package"
        
        if is_installed "$package"; then
            success_message "$package"
        else
            install_message "$package"
            if sudo apt-get install -y "$package" > /dev/null 2>&1; then
                success_message "$package"
            else
                error_message "$package"
            fi
        fi
    done

    # Notify user that the dependencies are installed
    echo -e "${GREEN}All dependencies are installed.${NC}"
}

# Function to install vagrant plugins
install_vagrant_plugins() {
    echo -e "${BLUE}Installing Vagrant plugins...${NC}"
    
    plugins=(
        "vagrant-reload"
        "vagrant-vbguest"
        "winrm"
        "winrm-fs"
        "winrm-elevated"
    )

    # Check if Vagrant is installed with vagrant plugin list
    if ! sudo -u $CURRENT_USER vagrant plugin list > /dev/null 2>&1; then
        echo -e "${RED}Vagrant is not installed. Please install Vagrant first.${NC}"
        exit 1
    fi

    installed_plugins=$(sudo -u $CURRENT_USER vagrant plugin list)

    # Check if the plugins are already installed
    for plugin in "${plugins[@]}"; do
        if echo "$installed_plugins" | grep -q "$plugin"; then
            echo -e "${GREEN}✔ $plugin is already installed.${NC}"
        else
            echo -e "${YELLOW}➜ Installing $plugin...${NC}"
            sudo -u $CURRENT_USER vagrant plugin install "$plugin" > /dev/null 2>&1
            echo -e "${GREEN}✔ $plugin is installed.${NC}"
        fi
    done

    # Notify user that the plugins are installed
    echo -e "${GREEN}All Vagrant plugins are installed.${NC}"
}

# Function to install Docker
install_docker() {
    echo -e "${BLUE}Installing Docker...${NC}"
    
    # Check if Docker is already installed
    if command -v docker > /dev/null; then
        echo -e "${GREEN}✔ Docker is already installed.${NC}"
    else
        echo -e "${YELLOW}➜ Installing Docker...${NC}"
        # Install Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        chown "$CURRENT_USER":"$CURRENT_USER" get-docker.sh
        sh get-docker.sh > /dev/null 2>&1
        rm get-docker.sh

        # Notify user that Docker is installed
        echo -e "${GREEN}✔ Docker is installed.${NC}"
    fi

    # Add user to docker group
    usermod -aG docker "$CURRENT_USER"
    
    # Notify user that Docker is installed
    echo -e "${GREEN}Docker is installed and '$CURRENT_USER' user is added to the docker group.${NC}"
}

# Function to create a new host-only network in VirtualBox
create_host_only_network() {
    echo -e "${BLUE}Creating host-only network in VirtualBox...${NC}"
    
    # Check to allow all networks address to use by the host-only network
    if grep -q "* 0.0.0.0/0 ::/0" /etc/vbox/networks.conf > /dev/null; then
        echo "Networks are already configured."
    else
        echo "Configuring networks..."
        mkdir -p /etc/vbox
        echo "* 0.0.0.0/0 ::/0" >> /etc/vbox/networks.conf
    fi

    # Check if the host-only network exists
    if VBoxManage list hostonlyifs | grep -q "Name:            $HOST_ONLY_NETWORK"; then
        echo "Host-only network '$HOST_ONLY_NETWORK' already exists. Removing..."
        VBoxManage hostonlyif remove "$HOST_ONLY_NETWORK"
    fi
    
    # Create a new host-only network
    VBoxManage hostonlyif create
    VBoxManage hostonlyif ipconfig "$HOST_ONLY_NETWORK" --ip "$HOST_ONLY_IP" --netmask "$HOST_ONLY_NETMASK"
    # Set the ip address for the host machine
    ifconfig "$HOST_ONLY_NETWORK" "$HOST_ONLY_IP" netmask "$HOST_ONLY_NETMASK" up
    
    # Notify user that the host-only network is created
    echo -e "${GREEN}Host-only network '$HOST_ONLY_NETWORK' is created with IP: $HOST_ONLY_IP.${NC}"
}

# Function to start and enable services
start_services() {
    echo -e "${BLUE}Starting and enabling services...${NC}"
    
    # Start and enable Docker services
    systemctl start docker > /dev/null 2>&1
    systemctl enable docker > /dev/null 2>&1

    # Notify user that services are started and enabled
    echo -e "${GREEN}Docker service is started and enabled.${NC}"

    # Start and enable Vagrant services
    systemctl start vagrant > /dev/null 2>&1
    systemctl enable vagrant > /dev/null 2>&1

    # Notify user that services are started and enabled
    echo -e "${GREEN}Vagrant service is started and enabled.${NC}"

    # Start and enable VirtualBox services
    systemctl start virtualbox.service > /dev/null 2>&1
    systemctl enable virtualbox.service > /dev/null 2>&1

    # Notify user that services are started and enabled
    echo -e "${GREEN}VirtualBox service is started and enabled.${NC}"
}

# Function to set up CAPEv2 Guest VM
setup_capev2_guest_vm() {
    echo -e "${BLUE}Setting up CAPEv2 Guest VM...${NC}"
    
    # wget sample VM Vagrant file
    wget $VAGRANTFILE_URL -O Vagrantfile || error_message "Failed to download Vagrantfile" || exit 1

    # Replace the placeholder with the actual values
    sed -i "s/REPLACE_VM_NAME/$VM_NAME/g" Vagrantfile
    sed -i "s/REPLACE_VM_CPU/$VM_CPUS/g" Vagrantfile
    sed -i "s/REPLACE_VM_RAM/$VM_RAM/g" Vagrantfile
    sed -i "s/REPLACE_VM_NETWORK/$VM_NETWORK/g" Vagrantfile
    sed -i "s/REPLACE_VM_ADAPTER/$VM_ADAPTER/g" Vagrantfile
    sed -i "s/REPLACE_VM_IP/$VM_IP/g" Vagrantfile
    sed -i "s/REPLACE_VM_SUBNET/$VM_SUBNET/g" Vagrantfile
    sed -i "s/REPLACE_VM_GW/$VM_GW/g" Vagrantfile
    sed -i "s/REPLACE_VM_DNS/$VM_DNS/g" Vagrantfile

    # Start the VM
    echo -e "${BLUE}Starting the CAPEv2 Guest VM. Waiting...${NC}"
    chown $CURRENT_USER:$CURRENT_USER Vagrantfile
    sudo -u $CURRENT_USER vagrant up --provider=virtualbox --no-provision

    # Install the guest additions
    echo -e "${BLUE}Installing the VirtualBox Guest Additions...${NC}"
    sudo -u $CURRENT_USER vagrant vbguest --do install --auto-reboot

    # Run the provisioning script
    echo -e "${BLUE}Running the provisioning script...${NC}"
    sudo -u $CURRENT_USER vagrant provision

    # Wait for the VM to be up. Check with ping
    while true; do
        echo -e "${YELLOW}Waiting for the VM to be up...${NC}"
        sleep 20
        # Attempt to ping the VM
        if ping -c 1 -W 1 "$VM_IP" &> /dev/null; then
            echo -e "${GREEN}✔ VM is up.${NC}"
            break
        fi
    done

    # Reload the VM without provisioning
    # echo -e "${BLUE}Reloading the VM without provisioning...${NC}"
    # sudo -u $CURRENT_USER vagrant reload --force --no-provision

    # Notify user that the CAPEv2 Guest VM is set up
    echo -e "${GREEN}CAPEv2 Guest VM is set up.${NC}"

    # Check if the snapshot already exists
    if sudo -u $CURRENT_USER VBoxManage snapshot "$VM_NAME" list | grep -q "$VM_SNAPSHOT"; then
        echo -e "${YELLOW}➜ Snapshot '$VM_SNAPSHOT' already exists.${NC}"
        echo -e "${YELLOW}➜ Removing the existing snapshot...${NC}"

        # List all snapshots and delete those that match the name
        for snapshot in $(sudo -u $CURRENT_USER VBoxManage snapshot "$VM_NAME" list | awk '{print $2}' | grep "$VM_SNAPSHOT"); do
            sudo -u $CURRENT_USER VBoxManage snapshot "$VM_NAME" delete "$snapshot"
            echo -e "${GREEN}➜ Deleted snapshot: '$snapshot'${NC}"
        done
    fi

    # Snapshot the VM
    echo -e "${BLUE}Taking a snapshot of the CAPEv2 Guest VM...${NC}"
    sudo -u $CURRENT_USER VBoxManage snapshot "$VM_NAME" take "$VM_SNAPSHOT" --pause

    # Notify user that the snapshot is taken
    echo -e "${GREEN}Snapshot '$VM_SNAPSHOT' taken for VM '$VM_NAME'.${NC}"
}


# Function to set up CAPEv2 on Docker
setup_capev2() {
    echo -e "${BLUE}Setting up CAPEv2 on Docker...${NC}"
    
    # Check if the CAPEv2 repository already exists
    if [ -d "cape-docker" ]; then
        echo -e "${YELLOW}➜ CAPEv2 repository already exists.${NC}"
        echo -e "${YELLOW}➜ Updating the CAPEv2 repository...${NC}"
        cd cape-docker || error_message "CAPEv2 repository not found." || exit 1
        git pull
        git submodule update --init --recursive
        cd $BASE_DIR
    else
        # Clone the CAPEv2 repository
        echo -e "${YELLOW}➜ Cloning the CAPEv2 repository...${NC}"
        git clone --recurse-submodules https://github.com/nquangit/cape-docker.git || error_message "Failed to clone the CAPEv2 repository." || exit 1
    fi

    # Change directory to the CAPEv2 repository
    cd cape-docker || error_message "CAPEv2 repository not found." || exit 1

    # Build the vbox-server
    echo -e "${BLUE}Building the vbox-server...${NC}"
    make vbox-server
    
    # Set up the vbox-server run as a service
    echo -e "${BLUE}Setting up the vbox-server as a service...${NC}"
    # Check if the vbox-socket-server service already exists
    if [ -f "/etc/systemd/system/vbox-socket-server.service" ]; then
        echo -e "${YELLOW}➜ vbox-socket-server service already exists.${NC}"
        echo -e "${YELLOW}➜ Reloading systemd services...${NC}"
        systemctl daemon-reload
    else
        # Create the vbox-socket-server service
        cat <<EOF > /etc/systemd/system/vbox-socket-server.service
[Unit]
Description=CAPEv2 vbox-socket-server
After=network.target

[Service]
Type=simple
ExecStart=$BASE_DIR/cape-docker/bin/vbox-server
WorkingDirectory=$BASE_DIR
Restart=always
RestartSec=3
User=$CURRENT_USER
Group=$CURRENT_USER

[Install]
WantedBy=multi-user.target
EOF

        # Reload systemd services
        systemctl daemon-reload
    fi

    # Start and enable the vbox-socket-server service
    systemctl start vbox-socket-server
    systemctl enable vbox-socket-server

    # Pull the latest Docker images
    sudo -u $CURRENT_USER docker pull celyrin/cape:latest

    # Change ownership of the cape-docker directory
    chown -R $CURRENT_USER:$CURRENT_USER .
    cd $BASE_DIR

    # Check if the container already exists
    if sudo -u $CURRENT_USER docker ps -a --format '{{.Names}}' | grep -q "cape"; then
        echo -e "${YELLOW}➜ CAPEv2 container already exists.${NC}"
        echo -e "${YELLOW}➜ Removing the existing CAPEv2 container...${NC}"
        sudo -u $CURRENT_USER docker rm -f cape
    fi

    # Remove old files in work directory
    rm -rf work

    # Start run the CAPEv2 on Docker
    echo -e "${BLUE}Starting CAPEv2 on Docker...${NC}"
    sudo -u $CURRENT_USER docker run -d \
        -v $(realpath ./vbox.sock):/opt/vbox/vbox.sock \
        --cap-add SYS_ADMIN -v /sys/fs/cgroup:/sys/fs/cgroup:rw --cgroupns=host\
        --tmpfs /run --tmpfs /run/lock \
        --net=host --cap-add=NET_RAW --cap-add=NET_ADMIN \
        --cap-add=SYS_NICE -v $(realpath ./work):/work \
        --name cape celyrin/cape:latest

    # Notify user that CAPEv2 is set up
    echo -e "${GREEN}CAPEv2 is set up on Docker.${NC}"
}

# Prepare configuration for CAPEv2 on Docker
override_cape_config() {
    # While loop to check if the work/conf/cuckoo.conf file exists
    while [ ! -f "work/conf/cuckoo.conf" ]; do
        echo -e "${YELLOW}work/conf/cuckoo.conf directory not found.${NC} Waiting..."
        sleep 3
        echo -e "${YELLOW}Checking the work/conf directory...${NC}"
    done

    echo -e "${BLUE}Preparing configuration for CAPEv2 on Docker...${NC}"
    
    # Backup the default configuration files
    cp work/conf/cuckoo.conf work/conf/cuckoo.conf.old
    cp work/conf/auxiliary.conf work/conf/auxiliary.conf.old
    mv work/conf/virtualbox.conf work/conf/virtualbox.conf.old

    # Download the CAPEv2 configuration files
    # wget https://raw.githubusercontent.com/kevoreilly/CAPEv2/refs/heads/master/conf/default/cuckoo.conf.default -O work/conf/cuckoo.conf || error_message "Failed to download cuckoo.conf.default" || exit 1
    # wget https://raw.githubusercontent.com/kevoreilly/CAPEv2/refs/heads/master/conf/default/auxiliary.conf.default -O work/conf/auxiliary.conf || error_message "Failed to download auxiliary.conf.default" || exit 1
    wget https://raw.githubusercontent.com/CyberSecN00bers/FPT_IAM302_Project/refs/heads/main/sandbox-config/work/conf/processing.conf -O work/conf/processing.conf || error_message "Failed to download processing.conf" || exit 1
    wget https://raw.githubusercontent.com/CyberSecN00bers/FPT_IAM302_Project/refs/heads/main/sandbox-config/work/conf/reporting.conf -O work/conf/reporting.conf || error_message "Failed to download reporting.conf" || exit 1
    wget https://raw.githubusercontent.com/CyberSecN00bers/FPT_IAM302_Project/refs/heads/main/sandbox-config/work/conf/cuckoo.conf -O work/conf/cuckoo.conf || error_message "Failed to download cuckoo.conf" || exit 1
    wget https://raw.githubusercontent.com/CyberSecN00bers/FPT_IAM302_Project/refs/heads/main/sandbox-config/work/conf/web.conf -O work/conf/web.conf || error_message "Failed to download web.conf" || exit 1
    wget https://raw.githubusercontent.com/CyberSecN00bers/FPT_IAM302_Project/refs/heads/main/sandbox-config/work/conf/check_service.sh -O work/conf/check_service.sh || error_message "Failed to download check_service.sh" || exit 1
    wget https://raw.githubusercontent.com/CyberSecN00bers/FPT_IAM302_Project/refs/heads/main/sandbox-config/work/conf/auxiliary.conf -O work/conf/auxiliary.conf || error_message "Failed to download auxiliary.conf" || exit 1

    # Replace the placeholder with the actual values
    echo -e "${BLUE}Replacing the placeholder with the actual values...${NC}"
    sed -i "s/machinery = kvm/machinery = virtualbox/g" work/conf/cuckoo.conf
    sed -i "s/ip = .*/ip = $HOST_ONLY_IP/g" work/conf/cuckoo.conf

    # interface = virbr1 to interface = $VM_NETWORK
    sed -i "s/interface = virbr1/interface = $VM_NETWORK/g" work/conf/auxiliary.conf

    # Enable the reporting module
    sed -i '/reporthtmlsummary/,/\[.*\]/ {
        s/enabled = no/enabled = yes/
    }' work/conf/reporting.conf

    # Create the virtualbox.conf file
    cat <<EOF > work/conf/virtualbox.conf
[virtualbox]
mode = gui
path = /usr/bin/VBoxManage
interface = $VM_NETWORK
machines = $VM_NAME

[$VM_NAME]
label = $VM_NAME
platform = windows
ip = $VM_IP
snapshot = $VM_SNAPSHOT
arch = x64
interface = $VM_NETWORK
resultserver_ip = $HOST_ONLY_IP
EOF

    # change ownership of the work directory
    # chown -R $CURRENT_USER:$CURRENT_USER work

    # Notify user that the configuration is prepared
    echo -e "${GREEN}Configuration for CAPEv2 on Docker is prepared.${NC}"
}

rerun_cape() {
    # Install optional dependencies
    echo -e "${BLUE}Installing optional dependencies...${NC}"
    sudo -u $CURRENT_USER docker exec -it cape /bin/bash -c "sudo apt install -y graphviz libgraphviz-dev"
    sudo -u $CURRENT_USER docker exec -it cape /bin/bash -c "sudo -u cape poetry run pip install \"pydantic>=2\" \"rich>=13\" \"pyparsing<3,>=2.1.0\""
    sudo -u $CURRENT_USER docker exec -it cape /bin/bash -c "sudo -u cape poetry run pip install -r extra/optional_dependencies.txt"
    # Restart cape service on docker
    echo -e "${BLUE}Restarting CAPEv2 on Docker...${NC}"
    sudo -u $CURRENT_USER docker exec -it cape /bin/bash -c "systemctl restart cape"
}

# MAIN SCRIPT
main() {
    # Check for internet connection
    check_internet

    # Check for apt package manager
    check_apt

    # Check for hardware virtualization support
    check_virtualization

    # Install dependencies
    install_dependencies

    # Install Vagrant plugins
    install_vagrant_plugins

    # Install Docker
    install_docker

    # Start and enable services
    start_services

    # Create a new host-only network in VirtualBox
    create_host_only_network

    # Set up CAPEv2 Guest VM
    setup_capev2_guest_vm

    # Set up CAPEv2 on Docker
    setup_capev2

    # Prepare configuration for CAPEv2 on Docker
    override_cape_config

    rerun_cape
}

main "$@"