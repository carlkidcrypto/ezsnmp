# Use CentOS 7 as the base image
FROM centos:7

# Fix for CentOS 7 EOL: Point repositories to the vault archive
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Update system and install essential tools
RUN yum update -y && \
    yum install -y yum-utils findutils

# Install the EPEL repository package
RUN yum install -y epel-release

# Update system and install essential tools
RUN yum update -y && \
    yum install -y yum-utils findutils

# Install the EPEL repository package
RUN yum install -y epel-release devtoolset-8

# Update system and install essential tools and build dependencies for Python
RUN yum update -y && \
    yum install -y yum-utils findutils gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make \
    unzip file  openssl net-snmp net-snmp-utils net-snmp-devel gcc-c++ gdb meson ninja-build gtest-devel \
    && yum clean all

# --- Build Python 3.9 from source ---
ENV PYTHON_VERSION=3.9.18
RUN wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

# Install debug symbols for relevant packages
RUN yum-config-manager --enable base-debuginfo && \
    debuginfo-install -y net-snmp-libs

# Manually create the pkg-config file for net-snmp by dynamically
# getting the correct flags and version from the system.
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