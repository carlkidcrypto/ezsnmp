# Use AlmaLinux 10-kitten as the base image
FROM almalinux:10-kitten

# Install EPEL, update system, and install dependencies in one layer to reduce image size
COPY dnf-requirements.txt /tmp/dnf-requirements.txt
RUN dnf install -y epel-release && \
    dnf update -y && \
    dnf install -y findutils && \
    xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Define the path for the virtual environment
ENV VENV_PATH=/opt/venv

# Create the virtual environment using Python 3.13
RUN python3.13 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
# All subsequent RUN, CMD, and ENTRYPOINT instructions will use this venv.
ENV PATH="$VENV_PATH/bin:$PATH"