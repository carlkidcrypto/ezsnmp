# Use AlmaLinux 10-kitten as the base image
FROM almalinux:10-kitten

# Define Python versions - the project supports 5 versions (latest + 4 older supported)
ARG PYTHON_MAX_VERSION=3.14.7
ARG PYTHON_MIN_2_VERSION=3.13.15  # Not built from source, provided by OS package manager
ARG PYTHON_MIN_1_VERSION=3.12.14  # Not built from source, provided by OS package manager
ARG PYTHON_MIN_0_VERSION=3.11.16
ARG PYTHON_MIN_VERSION=3.10.21

# Install EPEL, update system, and install dependencies in one layer to reduce image size
COPY docker/almalinux10_netsnmp_5.10/dnf-requirements.txt /tmp/dnf-requirements.txt
RUN dnf install -y epel-release && \
    dnf update -y && \
    dnf install -y findutils && \
    xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Copy and build NetSNMP 5.10.pre2 from cache
COPY docker/cache/net-snmp-5.10.pre2.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf net-snmp-5.10.pre2.tar.gz && \
    cd net-snmp-5.10.pre2 && \
    ./configure --prefix=/usr --enable-shared --disable-embedded-perl --without-perl-modules --with-mib-modules=mibII && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd /tmp && \
    rm -rf net-snmp-5.10.pre2.tar.gz net-snmp-5.10.pre2 && \
    net-snmp-config --version

# Create the pkg-config file for net-snmp (built from source above)
RUN LIBDIR=$(net-snmp-config --libdir | sed 's/^-L//') && \
    PREFIX=$(net-snmp-config --prefix) && \
    EXEC_PREFIX=$(net-snmp-config --exec-prefix) && \
    INCLUDEDIR=$(net-snmp-config --includedir | sed 's/^-I//') && \
    LIBS=$(net-snmp-config --libs | sed 's/[[:space:]]-lcrypto//g') && \
    CFLAGS=$(net-snmp-config --cflags | sed -e 's/[[:space:]]-Werror=declaration-after-statement//g' -e 's/[[:space:]]-Wstrict-prototypes//g') && \
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

# Copy Python tarballs from cache to avoid repeated downloads
COPY docker/cache/Python-3.10.21.tgz /tmp/
COPY docker/cache/Python-3.11.16.tgz /tmp/
COPY docker/cache/Python-3.14.7.tgz /tmp/

# Build Python 3.10, 3.11, 3.14 from source (not available in AlmaLinux 10 repos)
# AlmaLinux 10 only ships with Python 3.12 and 3.13
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

# Copy common DockerEntry.sh script
COPY docker/DockerEntry.sh /usr/local/bin/DockerEntry.sh
RUN chmod +x /usr/local/bin/DockerEntry.sh