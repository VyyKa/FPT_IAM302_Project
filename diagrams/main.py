from diagrams import Diagram, Cluster, Edge
from diagrams.digitalocean.compute import Containers
from diagrams.digitalocean.network import ManagedVpn, InternetGateway
from diagrams.generic.os import Windows, LinuxGeneral
from diagrams.generic.virtualization import Virtualbox
from diagrams.custom import Custom
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB


with Diagram("Malware Analysis", show=True, direction="LR"):
    with Cluster("Host", direction="RL"):
        socket_server = Custom("Socket Server", "./img/socket.png")

        with Cluster("VM Management"):
            virtualbox = Virtualbox("Virtualbox")
            vagrant = Custom("Vagrant", "./img/vagrant.png")
        
        virtual_nic = InternetGateway("Virtual NIC")

    with Cluster("Dockers", direction="RL"):
        with Cluster("CAPEv2"):
            cuckoo = Custom("Cuckoo host", "./img/cuckoo.png")

        api = Containers("UI/API")

    with Cluster("Virtualization"):
        with Cluster("Guest VMs", direction="TB"):
            guests = [Windows("Windows 10"), LinuxGeneral("Linux")]

        virtual_network = ManagedVpn("Virtual Network")

    # Edge
    api >> Edge(reverse=True) >> cuckoo

    vagrant >> Edge(color="darkgreen", reverse=True) >> virtualbox >> Edge(label="socket\ncommunication", reverse=True, color="darkorange") >> socket_server >> Edge(label="socket\ncommunication", reverse=True, color="darkorange") << cuckoo

    virtual_nic << Edge(reverse=True) << virtual_network >> Edge(color="red", reverse=True) >> guests

    virtualbox >> Edge(color="red", reverse=True) >> virtual_nic
    
    virtual_nic >> Edge(reverse=True) >> cuckoo