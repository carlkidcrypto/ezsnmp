# Use Fedora 41 as the base image
FROM fedora:41

# Define Python versions - the project supports 5 versions (latest + 4 older supported)
ARG PYTHON_MAX_VERSION=3.14.2
ARG PYTHON_MIN_2_VERSION=3.13.7
ARG PYTHON_MIN_1_VERSION=3.12.8
ARG PYTHON_MIN_0_VERSION=3.11.11
ARG PYTHON_MIN_VERSION=3.10.16

# Update system and install GCC (native GCC 14.x on Fedora 41 - no toolset needed)
RUN dnf update -y && \
    dnf install -y gcc gcc-c++ findutils

# Install remaining dependencies from requirements file
COPY docker/fedora41_netsnmp_5.7/dnf-requirements.txt /tmp/dnf-requirements.txt
RUN xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Build OpenSSL 1.0.2u from cache (required for net-snmp 5.7.3)
# Installed to /usr/local/openssl10 to avoid conflicting with system OpenSSL 3.x
COPY docker/cache/openssl-1.0.2u.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf openssl-1.0.2u.tar.gz && \
    cd openssl-1.0.2u && \
    ./Configure linux-x86_64 shared --prefix=/usr/local/openssl10 && \
    make && make install_sw && \
    echo "/usr/local/openssl10/lib" > /etc/ld.so.conf.d/openssl10.conf && ldconfig && \
    cd /tmp && rm -rf openssl-1.0.2u.tar.gz openssl-1.0.2u

ENV LD_LIBRARY_PATH="/usr/local/openssl10/lib:${LD_LIBRARY_PATH:-}"

# Copy and build NetSNMP 5.7.3 from cache
# Uses OpenSSL 1.0.2u built above, -j1 and MALLOC_CHECK_=0 for stability
COPY docker/cache/net-snmp-5.7.3.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf net-snmp-5.7.3.tar.gz && \
    cd net-snmp-5.7.3 && \
    ./configure --prefix=/usr \
        --enable-shared \
        --disable-embedded-perl \
        --without-perl-modules \
        --with-defaults \
        --with-sys-contact="root@localhost" \
        --with-sys-location="Unknown" \
        --with-logfile=/var/log/snmpd.log \
        --with-persistent-directory=/var/net-snmp \
        --disable-debugging \
        --with-openssl=/usr/local/openssl10 \
        --with-security-modules="tsm,usm" && \
    MALLOC_CHECK_=0 make -j1 && \
    MALLOC_CHECK_=0 make install && \
    ldconfig && \
    cd /tmp && \
    rm -rf net-snmp-5.7.3.tar.gz net-snmp-5.7.3 && \
    if ! snmpd -v 2>&1 | grep -q "5.7.3"; then echo "ERROR: Net-SNMP 5.7.3 not installed correctly"; exit 1; fi

ENV MALLOC_CHECK_=0

# Copy Python tarballs from cache to avoid repeated downloads
COPY docker/cache/Python-3.10.16.tgz /tmp/
COPY docker/cache/Python-3.11.11.tgz /tmp/
COPY docker/cache/Python-3.12.8.tgz /tmp/
COPY docker/cache/Python-3.13.7.tgz /tmp/
COPY docker/cache/Python-3.14.2.tgz /tmp/

# Build Python from source (all versions, split into separate layers for caching)

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
