#!/bin/bash -e

CONTAINER_NAME="snmp_container"
sudo chown carlkidcrypto /var/run/docker.sock
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

# Allow time for the container to start
# and install the dependencies
for i in {120..1}; do
    echo -ne "Waiting for container to start... $i seconds remaining\r"
    sleep 1
done
echo -ne "\n"

# Join the container
docker exec -it snmp_container /bin/bash
# docker logs snmp_container --details