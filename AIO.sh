#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root or use sudo."
    exit 1
fi

BASE_DIR=$(pwd)

# VM variables
VM_NAME="cybersec_windows_10"
VM_SNAPSHOT="snapshot1"
VM_CPUS=2
VM_RAM=4096
VM_NETWORK="vboxnet0"
VM_ADAPTER="Ethernet"
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
    systemctl start vboxautostart-service > /dev/null 2>&1
    systemctl enable vboxautostart-service > /dev/null 2>&1

    # Notify user that services are started and enabled
    echo -e "${GREEN}VirtualBox service is started and enabled.${NC}"
}

# Function to set up CAPEv2 Guest VM
setup_capev2_guest_vm() {
    echo -e "${BLUE}Setting up CAPEv2 Guest VM...${NC}"
    
    # wget sample VM Vagrant file
    wget https://gist.githubusercontent.com/nquangit/83633b69f28757217b1222d112b1a4c3/raw/68713bcc3930fb131559ce06bcda08b137475c9d/Vagrant -O Vagrantfile

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
    sudo -u $CURRENT_USER vagrant up --provider=virtualbox

    # Install the guest additions
    echo -e "${BLUE}Installing the VirtualBox Guest Additions...${NC}"
    sudo -u $CURRENT_USER vagrant vbguest --do install --auto-reboot

    # Run the provisioning script
    echo -e "${BLUE}Running the provisioning script...${NC}"
    sudo -u $CURRENT_USER vagrant provision

    # Notify user that the CAPEv2 Guest VM is set up
    echo -e "${GREEN}CAPEv2 Guest VM is set up.${NC}"

    # Snapshot the VM
    echo -e "${BLUE}Taking a snapshot of the CAPEv2 Guest VM...${NC}"
    VBoxManage snapshot "$VM_NAME" take "$VM_SNAPSHOT" --pause

    # Notify user that the snapshot is taken
    echo -e "${GREEN}Snapshot '$VM_SNAPSHOT' taken for VM '$VM_NAME'.${NC}"
}

# Prepare configuration for CAPEv2 on Docker
prepare_capev2_docker() {
    echo -e "${BLUE}Preparing configuration for CAPEv2 on Docker...${NC}"
    
    # Create a directory for CAPEv2 configuration
    mkdir -p work/conf

    # Download the CAPEv2 configuration files
    wget https://raw.githubusercontent.com/kevoreilly/CAPEv2/refs/heads/master/conf/default/cuckoo.conf.default -O work/conf/cuckoo.conf
    wget https://raw.githubusercontent.com/kevoreilly/CAPEv2/refs/heads/master/conf/default/auxiliary.conf.default -O work/conf/auxiliary.conf
    
    # Replace the placeholder with the actual values
    sed -i "s/machinery = kvm/machinery = virtualbox/g" work/conf/cuckoo.conf
    sed -i "s/ip = \*/ip = $HOST_ONLY_IP #/g" work/conf/cuckoo.conf

    # interface = virbr1 to interface = $VM_NETWORK
    sed -i "s/interface = virbr1/interface = $VM_NETWORK/g" work/conf/cuckoo.conf

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
    chown -R $CURRENT_USER:$CURRENT_USER work

    # Notify user that the configuration is prepared
    echo -e "${GREEN}Configuration for CAPEv2 on Docker is prepared.${NC}"
}


# Function to set up CAPEv2 on Docker
setup_capev2() {
    echo -e "${BLUE}Setting up CAPEv2 on Docker...${NC}"
    
    # Clone the CAPEv2 repository
    git clone --recurse-submodules https://github.com/nquangit/cape-docker

    # Change directory to the CAPEv2 repository
    cd cape-docker || error_message "CAPEv2 repository not found." && exit 1

    # Build the vbox-server
    echo -e "${BLUE}Building the vbox-server...${NC}"
    make vbox-server
    
    # Pull the latest Docker images
    docker pull celyrin/cape:latest

    # Change ownership of the cape-docker directory
    chown -R $CURRENT_USER:$CURRENT_USER .

    # Notify user that CAPEv2 is set up
    echo -e "${GREEN}CAPEv2 is set up on Docker.${NC}"
}

# MAIN SCRIPT

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

# Prepare configuration for CAPEv2 on Docker
prepare_capev2_docker

# Set up CAPEv2 on Docker
setup_capev2
