# Use CentOS 7 as the base image
FROM centos:7

# Fix for CentOS 7 EOL: Point repositories to the vault archive
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Install EPEL and Software Collections (SCL)
RUN yum install -y epel-release centos-release-scl

# Fix 1: Rerun sed commands on newly installed SCL repo files
RUN sed -i 's/^mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i -e 's|^#baseurl=|baseurl=|g' -e 's|mirror.centos.org|vault.centos.org|g' -e 's|https://vault.centos.org|http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Fix 2: Permanently disable the failing centos-sclo-sclo repo
RUN yum-config-manager --disable centos-sclo-sclo

# Update system
RUN yum update -y && yum clean all

# Install devtoolset-9 (GCC 9) and all build dependencies, including lcov
RUN yum install -y yum-utils findutils \
    devtoolset-9-gcc devtoolset-9-gcc-c++ devtoolset-9-binutils \
    openssl-devel bzip2-devel libffi-devel zlib-devel wget make \
    unzip file openssl net-snmp net-snmp-utils net-snmp-devel gdb meson ninja-build gtest-devel \
    lcov \
    && yum clean all

# Fix 3: PERSISTENT devtoolset-9 PATH for non-login shells (Crucial for meson/ninja tests)
RUN echo 'export PATH=/opt/rh/devtoolset-9/root/usr/bin/:$PATH' > /etc/profile.d/devtoolset.sh && \
    chmod +x /etc/profile.d/devtoolset.sh

# --- Build Multiple Python Versions from Source (Optimizations DISABLED to fix SystemError) ---

# Build Python 3.9.18
RUN PYTHON_VERSION=3.9.18 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-shared && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

# Build Python 3.10.13
RUN PYTHON_VERSION=3.10.13 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-shared && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

# Build Python 3.11.8 (FIXED: --enable-optimizations removed)
RUN PYTHON_VERSION=3.11.8 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-shared && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

# Build Python 3.12.3
RUN PYTHON_VERSION=3.12.3 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-shared && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

# Build Python 3.13.0
RUN PYTHON_VERSION=3.13.0 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-shared && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

# --- End Python Builds ---

# Install net-snmp debug symbols
RUN yum-config-manager --enable base-debuginfo && \
    debuginfo-install -y net-snmp-libs

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

# Create the virtual environment using the latest compiled python3.13
RUN python3.13 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
ENV PATH="$VENV_PATH/bin:$PATH"

# --- FINAL IMAGE CLEANUP (Marks image as final) ---
# # Removes temporary files, build tools, and caches to reduce image size.
# RUN yum remove -y wget devtoolset-9-gcc devtoolset-9-gcc-c++ devtoolset-9-binutils \
#     && rm -rf /var/cache/yum \
#     /usr/local/src/* \
#     /tmp/*