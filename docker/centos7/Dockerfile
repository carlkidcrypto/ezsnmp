# Use CentOS 7 as the base image
FROM centos:7

# Fix for CentOS 7 EOL: Point repositories to the vault archive
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Install EPEL and Software Collections (SCL)
RUN yum install -y epel-release centos-release-scl

# Fix: Rerun sed commands on newly installed SCL repo files
RUN sed -i 's/^mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i -e 's|^#baseurl=|baseurl=|g' -e 's|mirror.centos.org|vault.centos.org|g' -e 's|https://vault.centos.org|http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Fix: Permanently disable the failing centos-sclo-sclo repo
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

# --- CRITICAL FIX 3: PERSISTENT devtoolset-9 PATH for all commands ---
# This ensures that all future commands (tests, etc.) run in the container 
# automatically have the newer GCC 9 in their PATH.
RUN echo 'export PATH=/opt/rh/devtoolset-9/root/usr/bin/:$PATH' > /etc/profile.d/devtoolset.sh && \
    chmod +x /etc/profile.d/devtoolset.sh

# Build Python 3.9 from source (uses GCC 9 via the updated system PATH)
ENV PYTHON_VERSION=3.9.18
RUN wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

    RUN PYTHON_VERSION=3.10.13 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

RUN PYTHON_VERSION=3.11.8 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

RUN PYTHON_VERSION=3.12.3 && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

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

# Create the virtual environment using the newly compiled python3.9
RUN python3.9 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
ENV PATH="$VENV_PATH/bin:$PATH"