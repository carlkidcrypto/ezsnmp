# Use AlmaLinux 10-kitten as the base image
FROM almalinux:10-kitten

# Install the EPEL repository package
RUN dnf install -y epel-release

# Update system
RUN dnf update -y

# Install required tools
RUN dnf install -y findutils

# Install dependencies
COPY dnf-requirements.txt /tmp/dnf-requirements.txt
RUN xargs dnf install -y < /tmp/dnf-requirements.txt && dnf clean all

# Define the path for the virtual environment
ENV VENV_PATH=/opt/venv

# Create the virtual environment
RUN python3 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
# All subsequent RUN, CMD, and ENTRYPOINT instructions will use this venv.
ENV PATH="$VENV_PATH/bin:$PATH"