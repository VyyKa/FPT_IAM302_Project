from diagrams import Diagram, Cluster, Edge
from diagrams.digitalocean.compute import Containers
from diagrams.digitalocean.network import ManagedVpn, InternetGateway
from diagrams.generic.os import Windows, LinuxGeneral
from diagrams.generic.virtualization import Virtualbox
from diagrams.generic.compute import Rack
from diagrams.custom import Custom
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

graph_attr = {
    "pad": "2.0",
    "splines": "ortho",
    "nodesep": "0.60",
    "ranksep": "0.75",
    "fontname": "Sans-Serif",
    "fontsize": "15",
    "fontcolor": "#2D3436",
}

node_attr = {
    "shape": "box",
    "style": "rounded",
    "fixedsize": "true",
    "width": "1.5",
    "height": "1.5",
    "labelloc": "b",
    "imagepos": "tc",
    "imagescale": "true",
    "fontname": "Sans-Serif",
    "fontsize": "13",
    "fontcolor": "#2D3436",
}

with Diagram(
    "Malware Analysis",
    show=True,
    direction="LR",
    curvestyle="ortho",
    outformat="png",
    strict=True,
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    with Cluster("Host", direction="RL"):
        socket_server = Custom("Socket Server", "./img/socket.png")

        with Cluster("VM Management"):
            virtualbox = Virtualbox("Virtualbox")
            vagrant = Custom("Vagrant", "./img/vagrant.png")

        virtual_nic = InternetGateway("Virtual NIC")

        hypervisor = Rack("Hypervisor")

    with Cluster("Dockers", direction="RL"):
        with Cluster("CAPEv2"):
            cuckoo = Custom("Cuckoo host", "./img/cuckoo.png")

        api = Containers("UI/API")

    with Cluster("Virtualization"):
        with Cluster("Guest VMs", direction="TB"):
            guests = [Windows("Windows 10"), LinuxGeneral("Linux")]

        virtual_network = ManagedVpn("Virtual Network")

    # Edge
    virtualbox >> Edge(reverse=True) >> hypervisor >> Edge(reverse=True) >> guests

    api >> Edge(reverse=True) >> cuckoo

    (
        vagrant
        >> Edge(color="darkgreen", reverse=True)
        >> virtualbox
        >> Edge(label="socket\ncommunication", reverse=True, color="darkorange")
        >> socket_server
        >> Edge(label="socket\ncommunication", reverse=True, color="darkorange")
        << cuckoo
    )

    (
        cuckoo
        >> Edge(color="red", reverse=True)
        >> virtual_nic
        >> Edge(color="red", reverse=True)
        >> virtual_network
        >> Edge(color="red", reverse=True)
        >> guests
    )
