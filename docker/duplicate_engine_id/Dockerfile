# Use the latest Ubuntu base image
FROM ubuntu:latest

# Update package lists and install required packages
RUN apt-get update && apt-get install -y \
    snmpd \
    openssl \
    libssl-dev \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    g++ \
    snmp \
    libsnmp-dev \
    snmp-mibs-downloader \
    && apt-get clean

# Create the /ezsnmp directory in the container
RUN mkdir -p /ezsnmp

# Set the working directory to /ezsnmp
WORKDIR /ezsnmp

# Clone the ezsnmp repository into the /ezsnmp directory in the container
RUN apt-get update && apt-get install -y git && apt-get clean
RUN git clone https://github.com/carlkidcrypto/ezsnmp.git /ezsnmp

RUN mkdir -p /ezsnmp/docker/duplicate_engine_id
COPY .  /ezsnmp/docker/duplicate_engine_id

ARG USERNAME
ARG USER_UID
ARG USER_GID

RUN echo "USERNAME=${USERNAME}" && \
    echo "USER_UID=${USER_UID}" && \
    echo "USER_GID=${USER_GID}"

# Convert build arguments into environment variables
ENV USERNAME=${USERNAME}
ENV USER_UID=${USER_UID}
ENV USER_GID=${USER_GID}

RUN echo "USERNAME=${USERNAME}" && \
    echo "USER_UID=${USER_UID}" && \
    echo "USER_GID=${USER_GID}"

RUN groupadd -f --gid ${USER_GID} ${USERNAME} && \
    useradd -o --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME}

# Set ownership for the working directory
WORKDIR /ezsnmp
RUN chown -R ${USERNAME}:${USERNAME} /ezsnmp

RUN echo "${USERNAME}:x:${USER_UID}:${USER_GID}::/home/${USERNAME}:/bin/bash" >> /etc/passwd
RUN echo "${USERNAME}:x:${USER_GID}:" >> /etc/group
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Create a Python virtual environment
RUN rm -rf /home/${USERNAME}/.venv

# Create a virtual environment in the /home/${USERNAME}/.venv directory
# This is where Python packages will be installed
RUN python3 -m venv /home/${USERNAME}/.venv

# Activate the virtual environment and upgrade pip
RUN /home/${USERNAME}/.venv/bin/pip install --upgrade pip

# Set the virtual environment's bin directory in the PATH
ENV PATH="/home/${USERNAME}/.venv/bin:$PATH"

# Change the ownership of the virtual environment directory
# to the newly created user
# This is necessary to ensure that the user has permission to install packages
# in the virtual environment
RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.venv

RUN mkdir -p /opt/venv/
RUN chown -R ${USERNAME}:${USERNAME} /opt/venv/
RUN chmod -R 777 /opt/venv/

# Switch to the newly created user
USER ${USERNAME}