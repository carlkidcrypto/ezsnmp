# Use Rocky Linux 8 as the base image
FROM rockylinux:8

# Update system, install essential tools, and configure repositories in one layer
RUN dnf update -y && \
    dnf install -y findutils dnf-plugins-core epel-release && \
    dnf config-manager --set-enabled powertools

# Install gcc-toolset-11 (GCC 11.3.1, g++ 11.3.1) and dependencies from requirements file
COPY docker/rockylinux8/dnf-requirements.txt /tmp/dnf-requirements.txt
RUN dnf install -y gcc-toolset-11-gcc gcc-toolset-11-gcc-c++ gcc-toolset-11-binutils && \
    xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf debuginfo-install -y python3 net-snmp-libs && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Set gcc-toolset-11 PATH persistently for non-login shells
ENV PATH="/opt/rh/gcc-toolset-11/root/usr/bin:$PATH"

# Build Python 3.10, 3.11, 3.12, 3.13, 3.14 from source (not available in Rocky 8 repos)
# Note: 3.14 is pre-release (alpha/beta) - update version as stable releases become available
RUN for PY_VER in 3.10.16:3.10 3.11.11:3.11 3.12.8:3.12 3.13.7:3.13 3.14.0a4:3.14; do \
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

# Manually create the pkg-config file for net-snmp
RUN LIBS=$(net-snmp-config --libs) && \
    CFLAGS=$(net-snmp-config --cflags) && \
    VERSION=$(rpm -q --queryformat '%{VERSION}' net-snmp-devel) && \
    mkdir -p /usr/lib64/pkgconfig && \
    echo "prefix=/usr" > /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "exec_prefix=\${prefix}" >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "libdir=\${exec_prefix}/lib64" >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "includedir=\${prefix}/include" >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "" >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "Name: netsnmp" >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "Description: A collection of libraries for SNMP applications." >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "Version: ${VERSION}" >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "Libs: ${LIBS}" >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo "Cflags: ${CFLAGS}" >> /usr/lib64/pkgconfig/netsnmp.pc

# Define the path for the virtual environment
ENV VENV_PATH=/opt/venv

# Create the virtual environment using Python 3.14
RUN python3.14 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
ENV PATH="$VENV_PATH/bin:$PATH"

# Install Python requirements for project and tests inside the virtualenv
COPY requirements.txt /tmp/requirements.txt
COPY python_tests/requirements.txt /tmp/python_tests_requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/python_tests_requirements.txt && \
    rm -f /tmp/requirements.txt /tmp/python_tests_requirements.txt