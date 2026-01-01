# Use AlmaLinux 10-kitten as the base image
FROM almalinux:10-kitten

# Install EPEL, update system, and install dependencies in one layer to reduce image size
COPY docker/almalinux10/dnf-requirements.txt /tmp/dnf-requirements.txt
RUN dnf install -y epel-release && \
    dnf update -y && \
    dnf install -y findutils && \
    xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Build Python 3.10, 3.11, 3.14 from source (not available in AlmaLinux 10 repos)
# AlmaLinux 10 only ships with Python 3.12 and 3.13
# Split into separate layers for better Docker caching - only rebuilds on version changes

# Build Python 3.10.16
RUN wget -q https://www.python.org/ftp/python/3.10.16/Python-3.10.16.tgz && \
    tar -xzf Python-3.10.16.tgz && \
    cd Python-3.10.16 && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-3.10.16.tgz Python-3.10.16

# Build Python 3.11.11
RUN wget -q https://www.python.org/ftp/python/3.11.11/Python-3.11.11.tgz && \
    tar -xzf Python-3.11.11.tgz && \
    cd Python-3.11.11 && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-3.11.11.tgz Python-3.11.11

# Build Python 3.14.2 (latest stable release)
RUN wget -q https://www.python.org/ftp/python/3.14.2/Python-3.14.2.tgz && \
    tar -xzf Python-3.14.2.tgz && \
    cd Python-3.14.2 && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-3.14.2.tgz Python-3.14.2

# Configure dynamic linker
RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/usr_local_lib.conf && ldconfig

# Define the path for the virtual environment
ENV VENV_PATH=/opt/venv

# Create the virtual environment using Python 3.14
RUN python3.14 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
# All subsequent RUN, CMD, and ENTRYPOINT instructions will use this venv.
ENV PATH="$VENV_PATH/bin:$PATH"

# Install Python requirements for project and tests inside the virtualenv
COPY requirements.txt /tmp/requirements.txt
COPY python_tests/requirements.txt /tmp/python_tests_requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/python_tests_requirements.txt && \
    rm -f /tmp/requirements.txt /tmp/python_tests_requirements.txt