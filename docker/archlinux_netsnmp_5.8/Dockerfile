# Use Arch Linux as the base image
FROM archlinux:latest

# Update system
RUN pacman -Syu --noconfirm

# Install core packages (base-devel for makepkg, git, go, and sudo for AUR build)
RUN pacman -S --noconfirm findutils base-devel python python-pip python-setuptools pacman-contrib git go sudo

# Install official repository dependencies
COPY pacman-requirements.txt /tmp/pacman-requirements.txt
RUN xargs pacman -S --noconfirm < /tmp/pacman-requirements.txt

# Perform the downgrade to net-snmp5.8 and its dependencies
RUN pacman -U https://archive.archlinux.org/packages/n/net-snmp/net-snmp-5.8-1-x86_64.pkg.tar.xz --noconfirm
RUN pacman -U https://archive.archlinux.org/packages/o/openssl-1.1/openssl-1.1-1.1.1.w-1-x86_64.pkg.tar.zst --noconfirm

# --- AUR Installation: Must be run as a non-root user ---
ARG USERNAME=builder
# Create non-root user and set workspace
RUN useradd -m -G wheel $USERNAME
WORKDIR /home/$USERNAME

# Configure passwordless sudo for the builder user (needed for makepkg -si and yay)
RUN echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/docker-builder

# Switch to the non-root user for all AUR operations
USER $USERNAME

# Clone, build, and install 'yay'
# Set MAKEFLAGS for parallel compilation to speed up the build.
RUN export MAKEFLAGS="-j$(nproc)" && \
    git clone https://aur.archlinux.org/yay.git && \
    cd yay && \
    makepkg -si --noconfirm

# Install AUR packages from requirements file using yay
COPY aur-requirements.txt /tmp/aur-requirements.txt
# Set MAKEFLAGS for parallel compilation again to speed up the build of AUR dependencies.
RUN export MAKEFLAGS="-j$(nproc)" && \
    xargs yay -S --noconfirm < /tmp/aur-requirements.txt

# --- Switch back to root for final setup ---
USER root
WORKDIR /

# Clean up package cache
RUN pacman -Scc --noconfirm

# Virtual Environment Setup
ENV VENV_PATH=/opt/venv

# Create virtual environment and add its bin directory to PATH
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"