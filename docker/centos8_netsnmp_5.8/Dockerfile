# Use CentOS 8 as the base image (vault.centos.org for EOL distro)
FROM centos:8

# Define Python versions - the project supports 5 versions (latest + 4 older supported)
ARG PYTHON_MAX_VERSION=3.14.2
ARG PYTHON_MIN_2_VERSION=3.13.7
ARG PYTHON_MIN_1_VERSION=3.12.8
ARG PYTHON_MIN_0_VERSION=3.11.11
ARG PYTHON_MIN_VERSION=3.10.16

# Fix for CentOS 8 EOL and configure repositories in one layer
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* && \
    dnf update -y && \
    dnf install -y epel-release && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Install gcc-toolset-11 (GCC 11.x, g++ 11.x) and dependencies from requirements file
COPY docker/centos8_netsnmp_5.8/dnf-requirements.txt /tmp/dnf-requirements.txt
RUN dnf install -y gcc-toolset-11-gcc gcc-toolset-11-gcc-c++ gcc-toolset-11-binutils && \
    xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf debuginfo-install -y python3 net-snmp-libs && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Set gcc-toolset-11 PATH persistently for non-login shells
ENV PATH="/opt/rh/gcc-toolset-11/root/usr/bin:$PATH"

# Copy Python tarballs from cache to avoid repeated downloads
COPY docker/cache/Python-3.10.16.tgz /tmp/
COPY docker/cache/Python-3.11.11.tgz /tmp/
COPY docker/cache/Python-3.12.8.tgz /tmp/
COPY docker/cache/Python-3.13.7.tgz /tmp/
COPY docker/cache/Python-3.14.2.tgz /tmp/

# Build Python 3.10, 3.11, 3.12, 3.13, 3.14 from source (not available in CentOS 8 repos)
# Split into separate layers for better Docker caching - only rebuilds on version changes

# Build Python ${PYTHON_MIN_VERSION}
RUN cd /tmp && \
    tar -xzf Python-${PYTHON_MIN_VERSION}.tgz && \
    cd Python-${PYTHON_MIN_VERSION} && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd /tmp && \
    rm -rf Python-${PYTHON_MIN_VERSION}.tgz Python-${PYTHON_MIN_VERSION}

# Build Python ${PYTHON_MIN_0_VERSION}
RUN cd /tmp && \
    tar -xzf Python-${PYTHON_MIN_0_VERSION}.tgz && \
    cd Python-${PYTHON_MIN_0_VERSION} && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd /tmp && \
    rm -rf Python-${PYTHON_MIN_0_VERSION}.tgz Python-${PYTHON_MIN_0_VERSION}

# Build Python ${PYTHON_MIN_1_VERSION}
RUN cd /tmp && \
    tar -xzf Python-${PYTHON_MIN_1_VERSION}.tgz && \
    cd Python-${PYTHON_MIN_1_VERSION} && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd /tmp && \
    rm -rf Python-${PYTHON_MIN_1_VERSION}.tgz Python-${PYTHON_MIN_1_VERSION}

# Build Python ${PYTHON_MIN_2_VERSION}
RUN cd /tmp && \
    tar -xzf Python-${PYTHON_MIN_2_VERSION}.tgz && \
    cd Python-${PYTHON_MIN_2_VERSION} && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd /tmp && \
    rm -rf Python-${PYTHON_MIN_2_VERSION}.tgz Python-${PYTHON_MIN_2_VERSION}

# Build Python ${PYTHON_MAX_VERSION} (latest stable release)
RUN cd /tmp && \
    tar -xzf Python-${PYTHON_MAX_VERSION}.tgz && \
    cd Python-${PYTHON_MAX_VERSION} && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd /tmp && \
    rm -rf Python-${PYTHON_MAX_VERSION}.tgz Python-${PYTHON_MAX_VERSION} && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/usr_local_lib.conf && \
    ldconfig

# Manually create the pkg-config file for net-snmp
RUN LIBS=$(net-snmp-config --libs) && \
    CFLAGS=$(net-snmp-config --cflags) && \
    VERSION=$(rpm -q --queryformat '%{VERSION}' net-snmp-devel) && \
    mkdir -p /usr/lib64/pkgconfig && \
    echo 'prefix=/usr' > /usr/lib64/pkgconfig/netsnmp.pc && \
    echo 'exec_prefix=${prefix}' >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo 'libdir=${exec_prefix}/lib64' >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo 'includedir=${prefix}/include' >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo '' >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo 'Name: netsnmp' >> /usr/lib64/pkgconfig/netsnmp.pc && \
    echo 'Description: A collection of libraries for SNMP applications.' >> /usr/lib64/pkgconfig/netsnmp.pc && \
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
    pip install meson ninja && \
    rm -f /tmp/requirements.txt /tmp/python_tests_requirements.txt

# Copy and install Google Test from cache (not available in CentOS 8 EOL repos)
COPY docker/cache/v1.15.2.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf v1.15.2.tar.gz && \
    cd googletest-1.15.2 && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local && \
    make -j$(nproc) && \
    make install && \
    cd /tmp && \
    rm -rf v1.15.2.tar.gz googletest-1.15.2 && \
    ldconfig

# Copy common DockerEntry.sh script
COPY docker/DockerEntry.sh /usr/local/bin/DockerEntry.sh
RUN chmod +x /usr/local/bin/DockerEntry.sh
