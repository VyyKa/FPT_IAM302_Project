#!/bin/bash

docker run -it --privileged \
    -v $(realpath ./vbox.sock):/opt/vbox/vbox.sock \
    --cap-add SYS_ADMIN -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
    --tmpfs /run --tmpfs /run/lock \
    --net=host --cap-add=NET_RAW --cap-add=NET_ADMIN \
    --cap-add=SYS_NICE -v $(realpath ./work):/work \
    --name cape celyrin/cape:latest
