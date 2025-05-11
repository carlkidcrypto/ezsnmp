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

export USERNAME=$(whoami)
export USER_UID=$(id -u)
export USER_GID=$(id -g)

docker build --build-arg USERNAME="$USERNAME" \
             --build-arg USER_UID="$USER_UID" \
             --build-arg USER_GID="$USER_GID" \
             .

# docker-compose build
docker-compose up -d

# Wait for all containers to start by checking their logs
WAIT_TIME=120
declare -A CONTAINER_STATUS

for CONTAINER_NAME in "${CONTAINERS[@]}"; do
    CONTAINER_STATUS["$CONTAINER_NAME"]=0
done

for i in $(seq $WAIT_TIME -1 1); do
    for CONTAINER_NAME in "${CONTAINERS[@]}"; do
        if [[ ${CONTAINER_STATUS["$CONTAINER_NAME"]} -eq 0 ]]; then
            if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "Starting SNMP daemon..."; then
                echo -ne "\n$CONTAINER_NAME started successfully in $((WAIT_TIME - i)) seconds.\n"
                CONTAINER_STATUS["$CONTAINER_NAME"]=1
            fi
        fi
    done

    # Check if all containers have started
    if [[ $(printf "%s\n" "${CONTAINER_STATUS[@]}" | grep -c 0) -eq 0 ]]; then
        break
    fi

    echo -ne "Waiting for containers to start... $i seconds remaining\r"
    sleep 1
done
echo -ne "\n"

# Show the last logs after waiting or early stop
docker logs snmp_container --details --tail 5

# Join the container
docker exec -it snmp_container /bin/bash