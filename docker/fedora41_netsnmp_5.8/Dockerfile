# Use Fedora 41 as the base image
FROM fedora:41

# Define Python versions - the project supports 5 versions (latest + 4 older supported)
ARG PYTHON_MAX_VERSION=3.14.3
ARG PYTHON_MIN_2_VERSION=3.13.12
ARG PYTHON_MIN_1_VERSION=3.12.13
ARG PYTHON_MIN_0_VERSION=3.11.15
ARG PYTHON_MIN_VERSION=3.10.20

# Update system and install GCC (native GCC 14.x on Fedora 41 - no toolset needed)
RUN dnf update -y && \
    dnf install -y gcc gcc-c++ findutils

# Install remaining dependencies from requirements file
COPY docker/fedora41_netsnmp_5.8/dnf-requirements.txt /tmp/dnf-requirements.txt
RUN xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Copy and build NetSNMP 5.8 from cache
# Build against system OpenSSL, use -j1 and MALLOC_CHECK_=0 for stability
COPY docker/cache/net-snmp-5.8.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf net-snmp-5.8.tar.gz && \
    cd net-snmp-5.8 && \
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
        --with-openssl \
        --with-security-modules="tsm,usm" && \
    MALLOC_CHECK_=0 make -j1 && \
    MALLOC_CHECK_=0 make install && \
    ldconfig && \
    cd /tmp && \
    rm -rf net-snmp-5.8.tar.gz net-snmp-5.8 && \
    if ! snmpd -v 2>&1 | grep -q "5.8"; then echo "ERROR: Net-SNMP 5.8 not installed correctly"; exit 1; fi

ENV MALLOC_CHECK_=0

# Copy Python tarballs from cache to avoid repeated downloads
COPY docker/cache/Python-3.10.20.tgz /tmp/
COPY docker/cache/Python-3.11.15.tgz /tmp/
COPY docker/cache/Python-3.12.13.tgz /tmp/
COPY docker/cache/Python-3.13.12.tgz /tmp/
COPY docker/cache/Python-3.14.3.tgz /tmp/

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
RUN LIBDIR=$(net-snmp-config --libdir) && \
    PREFIX=$(net-snmp-config --prefix) && \
    EXEC_PREFIX=$(net-snmp-config --exec-prefix) && \
    INCLUDEDIR=$(net-snmp-config --includedir) && \
    LIBS=$(net-snmp-config --libs) && \
    CFLAGS=$(net-snmp-config --cflags) && \
    VERSION=$(net-snmp-config --version) && \
    mkdir -p "${LIBDIR}/pkgconfig" && \
    echo "prefix=${PREFIX}" > "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo "exec_prefix=${EXEC_PREFIX}" >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo "libdir=${LIBDIR}" >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo "includedir=${INCLUDEDIR}" >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo '' >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo 'Name: netsnmp' >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo 'Description: A collection of libraries for SNMP applications.' >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo "Version: ${VERSION}" >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo "Libs: ${LIBS}" >> "${LIBDIR}/pkgconfig/netsnmp.pc" && \
    echo "Cflags: ${CFLAGS}" >> "${LIBDIR}/pkgconfig/netsnmp.pc"

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
