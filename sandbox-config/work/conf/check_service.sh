#!/bin/bash

# List of services to check
services=(
    "cape.service"
    "cape-processor.service"
    "cape-web.service"
    "cape-rooter.service"
)

# Loop through each service and check its status
for service in "${services[@]}"; do
    status=$(systemctl is-active "$service")
    
    case $status in
        active)
            echo "$service is running."
            ;;
        inactive)
            echo "$service is not running."
            ;;
        failed)
            echo "$service has failed."
            ;;
        unknown)
            echo "$service is not recognized."
            ;;
        *)
            echo "Status of $service: $status"
            ;;
    esac
done

