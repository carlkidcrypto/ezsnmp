# Use Arch Linux as the base image
FROM archlinux:latest

# Update system and install core packages in one layer
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm findutils base-devel python python-pip python-setuptools \
    pacman-contrib git go sudo gcc

# Install official repository dependencies
COPY pacman-requirements.txt /tmp/pacman-requirements.txt
RUN xargs pacman -S --noconfirm < /tmp/pacman-requirements.txt && \
    rm -f /tmp/pacman-requirements.txt

# Downgrade Net-SNMP to 5.8 and install dependencies
RUN pacman -U --noconfirm \
    https://archive.archlinux.org/packages/n/net-snmp/net-snmp-5.8-1-x86_64.pkg.tar.xz \
    https://archive.archlinux.org/packages/p/pcre/pcre-8.43-1-x86_64.pkg.tar.xz \
    https://archive.archlinux.org/packages/o/openssl-1.1/openssl-1.1-1.1.1.w-1-x86_64.pkg.tar.zst

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

# Build Python 3.9, 3.10, 3.11, 3.12 from source (system has 3.13 already)
# This is faster and more reliable than AUR packages
RUN for PY_VER in 3.9.21:3.9 3.10.16:3.10 3.11.11:3.11 3.12.8:3.12; do \
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
    ldconfig

# Virtual Environment Setup using latest Python (3.13)
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"