# Use the latest Ubuntu base image
FROM ubuntu:latest

# Update package lists and install required packages
RUN apt-get update && apt-get install -y \
    openssl \
    libssl-dev \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    g++ \
    iputils-ping \
    iproute2 \
    vim \
    wget \
    unzip \
    libtool \
    pkg-config \
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

RUN wget -O net-snmp.zip https://sourceforge.net/projects/net-snmp/files/net-snmp/5.9.4/net-snmp-5.9.4.zip/download && \
    unzip net-snmp.zip && \
    cd net-snmp-5.9.4 && \
    ./configure --with-defaults --with-mibs=all --disable-manual --without-perl-modules --disable-embedded-perl --with-openssl=/usr/lib/x86_64-linux-gnu/ && \
    make -j$(nproc) && \
    make install && \
    mkdir -p /usr/share/snmp/mibs && \
    cp -r mibs/* /usr/share/snmp/mibs/ && \
    echo "/usr/local/lib" >> /etc/ld.so.conf.d/net-snmp.conf && \
    ldconfig

# Set environment variables for the user
# These variables are used to create a non-root user in the container
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

# Ensure SNMP configuration directory exists
RUN mkdir -p /etc/snmp

# Switch to the newly created user
USER ${USERNAME}