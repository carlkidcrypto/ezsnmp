#!/bin/bash -e

CONTAINERS=("main_container" "second_container" "third_container")
sudo chown $USER /var/run/docker.sock
for CONTAINER_NAME in "${CONTAINERS[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker stop $CONTAINER_NAME
    fi
    docker rm -f $CONTAINER_NAME
done

# Check for optional parameter to clean old Docker stuff
if [[ "$1" == "--clean" ]]; then
    echo "Cleaning old Docker stuff..."
    docker system prune -af
fi

docker-compose build
docker-compose up -d

# Wait for the containers to start by checking their logs
WAIT_TIME=120
for CONTAINER_NAME in "${CONTAINERS[@]}"; do
    for i in $(seq $WAIT_TIME -1 1); do
        if docker logs $CONTAINER_NAME 2>&1 | grep -q "Starting SNMP daemon..."; then
            echo -ne "\n$CONTAINER_NAME started successfully in $((WAIT_TIME - i)) seconds.\n"
            break
        fi
        echo -ne "Waiting for $CONTAINER_NAME to start... $i seconds remaining\r"
        sleep 1
    done
    echo -ne "\n"

    # Show the last logs after waiting or early stop
    docker logs $CONTAINER_NAME --details --tail 5
done

# Join the container
docker exec -it snmp_container /bin/bash