# Use Rocky Linux 9 as the base image
FROM rockylinux:9

# Define Python versions - the project supports 5 versions (latest + 4 older supported)
ARG PYTHON_MAX_VERSION=3.14.2
ARG PYTHON_MIN_2_VERSION=3.13.7
ARG PYTHON_MIN_1_VERSION=3.12.8
ARG PYTHON_MIN_0_VERSION=3.11.11
ARG PYTHON_MIN_VERSION=3.10.16

# Update system, install essential tools, and configure repositories in one layer
RUN dnf update -y && \
    dnf install -y findutils dnf-plugins-core epel-release && \
    dnf config-manager --set-enabled crb

# Install gcc-toolset-13 (GCC 13.x, g++ 13.x) and dependencies from requirements file
COPY docker/rockylinux9_netsnmp_5.9/dnf-requirements.txt /tmp/dnf-requirements.txt
RUN dnf install -y gcc-toolset-13-gcc gcc-toolset-13-gcc-c++ gcc-toolset-13-binutils && \
    xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf debuginfo-install -y python3 && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Set gcc-toolset-13 PATH persistently for non-login shells
ENV PATH="/opt/rh/gcc-toolset-13/root/usr/bin:$PATH"

# Copy and build NetSNMP 5.9.4 from cache to ensure complete headers are available
# (RockyLinux 9's net-snmp-devel package 5.9.1 is missing netsnmp_cleanup_session declaration)
# Disable all Perl support to minimize image size and avoid perl-ExtUtils-MakeMaker dependency
COPY docker/cache/net-snmp-5.9.4.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf net-snmp-5.9.4.tar.gz && \
    cd net-snmp-5.9.4 && \
    ./configure --prefix=/usr --enable-shared --disable-embedded-perl --without-perl-modules && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd /tmp && \
    rm -rf net-snmp-5.9.4.tar.gz net-snmp-5.9.4 && \
    net-snmp-config --version

# Copy Python tarballs from cache to avoid repeated downloads
COPY docker/cache/Python-3.10.16.tgz /tmp/
COPY docker/cache/Python-3.11.11.tgz /tmp/
COPY docker/cache/Python-3.12.8.tgz /tmp/
COPY docker/cache/Python-3.13.7.tgz /tmp/
COPY docker/cache/Python-3.14.2.tgz /tmp/

# Build Python 3.10, 3.11, 3.12, 3.13, 3.14 from source (not available in Rocky 9 repos)
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

# Create the pkg-config file for net-snmp (built from source above)
RUN LIBS=$(net-snmp-config --libs) && \
    CFLAGS=$(net-snmp-config --cflags) && \
    VERSION=$(net-snmp-config --version) && \
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
    rm -f /tmp/requirements.txt /tmp/python_tests_requirements.txt

# Copy common DockerEntry.sh script
COPY docker/DockerEntry.sh /usr/local/bin/DockerEntry.sh
RUN chmod +x /usr/local/bin/DockerEntry.sh
