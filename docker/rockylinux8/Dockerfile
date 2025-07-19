# Use Rocky Linux 8 as the base image
FROM rockylinux:8

# Update system
RUN dnf update -y

# Install required tools
RUN dnf install -y findutils

# Install the EPEL repository package
RUN dnf install -y epel-release

# Install the dnf-plugins-core package to get the 'config-manager' tool
RUN dnf install -y dnf-plugins-core

# Enable the 'powertools' repository (all lowercase)
RUN dnf config-manager --set-enabled powertools

# Install dependencies
COPY dnf-requirements.txt /tmp/dnf-requirements.txt
RUN xargs dnf install -y < /tmp/dnf-requirements.txt && dnf clean all

# Now, USE the command to install debug symbols for the package you are debugging.
RUN debuginfo-install -y python3 net-snmp-libs

# Define the path for the virtual environment
ENV VENV_PATH=/opt/venv

# Create the virtual environment
RUN python3.9 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
# All subsequent RUN, CMD, and ENTRYPOINT instructions will use this venv.
ENV PATH="$VENV_PATH/bin:$PATH"
