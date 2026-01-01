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

# Build Python 3.12.8
RUN wget -q https://www.python.org/ftp/python/3.12.8/Python-3.12.8.tgz && \
    tar -xzf Python-3.12.8.tgz && \
    cd Python-3.12.8 && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-3.12.8.tgz Python-3.12.8

# Build Python 3.13.7
RUN wget -q https://www.python.org/ftp/python/3.13.7/Python-3.13.7.tgz && \
    tar -xzf Python-3.13.7.tgz && \
    cd Python-3.13.7 && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-3.13.7.tgz Python-3.13.7

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