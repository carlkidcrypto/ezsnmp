# Use Arch Linux as the base image
FROM archlinux:latest

# Define Python versions - the project supports 5 versions (latest + 4 older supported)
ARG PYTHON_MAX_VERSION=3.14.2
ARG PYTHON_MIN_2_VERSION=3.13.7  # Not built from source, provided by OS package manager
ARG PYTHON_MIN_1_VERSION=3.12.8
ARG PYTHON_MIN_0_VERSION=3.11.11
ARG PYTHON_MIN_VERSION=3.10.16

# Update system and install core packages in one layer
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm findutils base-devel python python-pip python-setuptools \
    pacman-contrib git go sudo gcc

# Install official repository dependencies
COPY docker/archlinux_netsnmp_5.7/pacman-requirements.txt /tmp/pacman-requirements.txt
RUN xargs pacman -S --noconfirm < /tmp/pacman-requirements.txt && \
    rm -f /tmp/pacman-requirements.txt

# Copy OpenSSL 1.0.2u from cache (needed for Net-SNMP 5.7.3 OpenSSL APIs)
COPY docker/cache/openssl-1.0.2u.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf openssl-1.0.2u.tar.gz && \
    cd openssl-1.0.2u && \
    ./Configure linux-x86_64 shared --prefix=/usr/local/openssl10 && \
    make && make install_sw && \
    echo "/usr/local/openssl10/lib" > /etc/ld.so.conf.d/openssl10.conf && ldconfig && \
    cd /tmp && rm -rf openssl-1.0.2u.tar.gz openssl-1.0.2u

# Copy and build Net-SNMP 5.7.3 from cache, link against OpenSSL 1.0.2u
# Disable embedded perl, and avoid parallel build to prevent race issues
COPY docker/cache/net-snmp-5.7.3.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf net-snmp-5.7.3.tar.gz && \
    cd net-snmp-5.7.3 && \
    ./configure --prefix=/usr --enable-shared --disable-embedded-perl --without-perl-modules --with-openssl=/usr/local/openssl10 && \
    make && \
    make install && \
    ldconfig && \
    cd /tmp && \
    rm -rf net-snmp-5.7.3.tar.gz net-snmp-5.7.3 && \
    # Verify installation
    if ! snmpd -v 2>&1 | grep -q "5.7.3"; then echo "ERROR: Net-SNMP 5.7.3 not installed correctly"; exit 1; fi && \
    # Create pkg-config metadata
    mkdir -p /usr/lib/pkgconfig && \
    cat >/usr/lib/pkgconfig/netsnmp.pc <<'EOF'
prefix=/usr
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include

Name: Net-SNMP
Description: SNMP client and agent libraries
Version: 5.7.3
Libs: -L${libdir} -lnetsnmp -lcrypto
Cflags: -I${includedir}
EOF

# --- AUR Installation: Must be run as a non-root user ---
ARG USERNAME=builder
RUN useradd -m -G wheel $USERNAME && \
    echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/docker-builder

WORKDIR /home/$USERNAME
USER $USERNAME

# Clone, build, and install 'yay' with parallel compilation
RUN export MAKEFLAGS="-j$(nproc)" && \
    git clone --depth=1 https://aur.archlinux.org/yay.git && \
    cd yay && \
    makepkg -si --noconfirm && \
    cd .. && \
    rm -rf yay

# Note: All packages now available in official repos, no AUR packages needed

# --- Switch back to root for final setup ---
USER root
WORKDIR /

# Clean up package cache to reduce image size
RUN pacman -Scc --noconfirm && \
    rm -rf /home/$USERNAME/.cache

# Copy Python tarballs from cache to avoid repeated downloads
COPY docker/cache/Python-3.10.16.tgz /tmp/
COPY docker/cache/Python-3.11.11.tgz /tmp/
COPY docker/cache/Python-3.12.8.tgz /tmp/
COPY docker/cache/Python-3.13.7.tgz /tmp/
COPY docker/cache/Python-3.14.2.tgz /tmp/

# Build Python 3.10, 3.11, 3.12, 3.13, 3.14 from source
# This is faster and more reliable than AUR packages
# altinstall puts binaries as python3.X in /usr/local/bin
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
    ldconfig

# Ensure tox can find all Python versions by adding /usr/local/bin to PATH first
# Also add /usr/local/lib to LD_LIBRARY_PATH for shared library loading
ENV PATH="/usr/local/bin:$PATH"
ENV LD_LIBRARY_PATH="/usr/local/lib"

# Virtual Environment Setup using latest Python (3.14)
ENV VENV_PATH=/opt/venv
RUN python3.14 -m venv $VENV_PATH
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