#!/bin/bash -e

CONTAINER_NAME="snmp_container"
sudo chown carlkidcrypto /var/run/docker.sock
docker stop $CONTAINER_NAME
docker rm -f $CONTAINER_NAME

# Clean old docker stuff
# docker system prune -af
docker-compose build
docker-compose up -d

# Allow time for the container to start
# and install the dependencies
sleep 60

# Join the container
docker exec -it snmp_container /bin/bash
# docker logs snmp_container --details