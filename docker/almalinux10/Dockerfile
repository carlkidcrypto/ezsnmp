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
# Note: 3.14 is pre-release (alpha/beta) - update version as stable releases become available
RUN for PY_VER in 3.10.16:3.10 3.11.11:3.11 3.14.0a4:3.14; do \
        FULL_VERSION=${PY_VER%%:*}; \
        SHORT_VERSION=${PY_VER##*:}; \
        wget -q https://www.python.org/ftp/python/$FULL_VERSION/Python-$FULL_VERSION.tgz && \
        tar -xzf Python-$FULL_VERSION.tgz && \
        cd Python-$FULL_VERSION && \
        ./configure --enable-shared && \
        make -j$(nproc) altinstall && \
        cd .. && \
        rm -rf Python-$FULL_VERSION.tgz Python-$FULL_VERSION; \
    done && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/usr_local_lib.conf && \
    ldconfig

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