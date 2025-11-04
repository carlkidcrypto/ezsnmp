# Use Rocky Linux 8 as the base image
FROM rockylinux:8

# Update system, install essential tools, and configure repositories in one layer
RUN dnf update -y && \
    dnf install -y findutils dnf-plugins-core epel-release && \
    dnf config-manager --set-enabled powertools

# Install dependencies from requirements file
COPY dnf-requirements.txt /tmp/dnf-requirements.txt
RUN xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf debuginfo-install -y python3 net-snmp-libs && \
    dnf clean all && \
    rm -rf /var/cache/dnf /tmp/dnf-requirements.txt

# Build Python 3.13 from source (not available in Rocky 8 repos)
RUN PYTHON_VERSION=3.13.1 && \
    dnf install -y bzip2-devel libffi-devel zlib-devel && \
    wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xzf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --enable-shared --enable-optimizations && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/usr_local_lib.conf && \
    ldconfig

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

# Create the virtual environment using Python 3.13
RUN python3.13 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
ENV PATH="$VENV_PATH/bin:$PATH"