#!/bin/bash -e

CONTAINER_NAME="snmp_container"
sudo chown $USER /var/run/docker.sock
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker stop $CONTAINER_NAME
fi
docker rm -f $CONTAINER_NAME

# Check for optional parameter to clean old Docker stuff
if [[ "$1" == "--clean" ]]; then
    echo "Cleaning old Docker stuff..."
    docker system prune -af
fi

docker-compose build
docker-compose up -d

# Wait for the container to start by checking its logs
WAIT_TIME=120
for i in $(seq $WAIT_TIME -1 1); do
    if docker logs snmp_container 2>&1 | grep -q "Starting SNMP daemon..."; then
        echo -ne "\nContainer started successfully in $((WAIT_TIME - i)) seconds.\n"
        break
    fi
    echo -ne "Waiting for container to start... $i seconds remaining\r"
    sleep 1
done
echo -ne "\n"

# Show the last logs after waiting or early stop
docker logs snmp_container --details --tail 5

# Join the container
docker exec -it snmp_container /bin/bash