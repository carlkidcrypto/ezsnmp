# Use Arch Linux as the base image
FROM archlinux:latest

# Update system and install core packages in one layer
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm findutils base-devel python python-pip python-setuptools \
    pacman-contrib git go sudo gcc

# Install official repository dependencies
COPY docker/archlinux_netsnmp_5.8/pacman-requirements.txt /tmp/pacman-requirements.txt
RUN xargs pacman -S --noconfirm < /tmp/pacman-requirements.txt && \
    rm -f /tmp/pacman-requirements.txt

# Downgrade Net-SNMP to 5.8 and install legacy dependencies (PCRE 8, OpenSSL 1.1)
# Keep current Perl (from earlier install) and fabricate compatibility paths for libperl expected by net-snmp 5.8.
RUN pacman -U --noconfirm \
    https://archive.archlinux.org/packages/n/net-snmp/net-snmp-5.8-1-x86_64.pkg.tar.xz \
    https://archive.archlinux.org/packages/p/pcre/pcre-8.43-1-x86_64.pkg.tar.xz \
    https://archive.archlinux.org/packages/o/openssl-1.1/openssl-1.1-1.1.1.w-1-x86_64.pkg.tar.zst && \
    ldconfig && \
    PERL_CORE_DIR=$(perl -MConfig -e 'print $Config{archlib} . "/CORE"') && \
    mkdir -p /usr/lib/perl5/5.28/core_perl && \
    ln -sf "$PERL_CORE_DIR" /usr/lib/perl5/5.28/core_perl/CORE && \
    if [ -f "$PERL_CORE_DIR/libperl.so" ]; then ln -sf "$PERL_CORE_DIR/libperl.so" /usr/lib/libperl.so; fi && \
    ldconfig && \
    # Verify netsnmp headers exist and create pkg-config metadata
    if [ ! -d /usr/include/net-snmp ]; then echo "WARNING: /usr/include/net-snmp not found"; fi && \
    mkdir -p /usr/lib/pkgconfig && \
    cat >/usr/lib/pkgconfig/netsnmp.pc <<'EOF'
prefix=/usr
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include

Name: Net-SNMP
Description: SNMP client and agent libraries
Version: 5.8
Libs: -L${libdir} -lnetsnmp -lcrypto
Libs.private: -lwrap
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

# Build Python 3.10, 3.11, 3.12, 3.14 from source (system has 3.13 already)
# This is faster and more reliable than AUR packages
# altinstall puts binaries as python3.X in /usr/local/bin
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

# Build Python 3.14.2 (latest stable release)
RUN wget -q https://www.python.org/ftp/python/3.14.2/Python-3.14.2.tgz && \
    tar -xzf Python-3.14.2.tgz && \
    cd Python-3.14.2 && \
    ./configure --enable-shared && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-3.14.2.tgz Python-3.14.2

# Configure dynamic linker
RUN ldconfig

# Ensure tox can find all Python versions by adding /usr/local/bin to PATH first
ENV PATH="/usr/local/bin:$PATH"

# Ensure pkg-config finds netsnmp 5.8
ENV PKG_CONFIG_PATH="/usr/lib/pkgconfig:$PKG_CONFIG_PATH"

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