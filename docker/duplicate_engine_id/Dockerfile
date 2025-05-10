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

# Create a Python virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and upgrade pip
RUN /opt/venv/bin/pip install --upgrade pip

# Set the virtual environment's bin directory in the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Create the /ezsnmp directory in the container
RUN mkdir -p /ezsnmp

# Set the working directory to /ezsnmp
WORKDIR /ezsnmp

# Clone the ezsnmp repository into the /ezsnmp directory in the container
RUN apt-get update && apt-get install -y git && apt-get clean
RUN git clone https://github.com/carlkidcrypto/ezsnmp.git /ezsnmp

RUN mkdir -p /ezsnmp/docker/duplicate_engine_id
COPY .  /ezsnmp/docker/duplicate_engine_id

# Switch to the user specified by the ${USER} environment variable
USER ${USER}