# Use CentOS 7 as the base image
FROM centos:7

# Fix for CentOS 7 EOL and install EPEL/SCL in one layer
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* && \
    yum install -y epel-release centos-release-scl openssl-devel && \
    sed -i 's/^mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i -e 's|^#baseurl=|baseurl=|g' -e 's|mirror.centos.org|vault.centos.org|g' -e 's|https://vault.centos.org|http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* && \
    yum-config-manager --disable centos-sclo-sclo && \
    yum update -y && \
    yum clean all

# Install devtoolset-11 (GCC 11.2.1, g++ 11.2.1) and all build dependencies in one layer
RUN yum install -y yum-utils findutils \
    devtoolset-11-gcc devtoolset-11-gcc-c++ devtoolset-11-binutils \
    openssl-devel bzip2-devel libffi-devel zlib-devel sqlite-devel wget make \
    unzip file openssl net-snmp net-snmp-utils net-snmp-devel gdb meson ninja-build gtest-devel lcov && \
    yum clean all && \
    rm -rf /var/cache/yum

# Set devtoolset-11 PATH persistently for non-login shells
ENV PATH="/opt/rh/devtoolset-11/root/usr/bin:$PATH"

# Build modern OpenSSL (CentOS 7 ships 1.0.2 which is too old for Python >=3.13 SSL module)
RUN mkdir -p /tmp/build && cd /tmp/build && \
    wget -q https://www.openssl.org/source/openssl-1.1.1w.tar.gz && \
    tar -xzf openssl-1.1.1w.tar.gz && \
    cd openssl-1.1.1w && \
    ./Configure linux-x86_64 no-shared --prefix=/usr/local/openssl && \
    make -j$(nproc) && \
    make install_sw && \
    cd / && rm -rf /tmp/build && \
    echo "/usr/local/openssl/lib" > /etc/ld.so.conf.d/openssl_local.conf && ldconfig

# Build Python 3.10.16, 3.11.11, 3.12.8, 3.13.7 from source with OpenSSL 1.1.1w
# Note: --enable-optimizations disabled due to coverage profiling conflicts
RUN for PY_VER in 3.10.16:3.10 3.11.11:3.11 3.12.8:3.12 3.13.7:3.13; do \
        FULL_VERSION=${PY_VER%%:*}; \
        SHORT_VERSION=${PY_VER##*:}; \
        wget -q https://www.python.org/ftp/python/$FULL_VERSION/Python-$FULL_VERSION.tgz && \
        tar -xzf Python-$FULL_VERSION.tgz && \
        cd Python-$FULL_VERSION && \
        ./configure --enable-shared --with-openssl=/usr/local/openssl && \
        make -j$(nproc) altinstall && \
        cd .. && \
        rm -rf Python-$FULL_VERSION.tgz Python-$FULL_VERSION; \
    done && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/usr_local_lib.conf && \
    ldconfig

# Install net-snmp debug symbols and create pkg-config file
RUN yum-config-manager --enable base-debuginfo && \
    debuginfo-install -y net-snmp-libs && \
    yum clean all && \
    LIBS=$(net-snmp-config --libs) && \
    CFLAGS=$(net-snmp-config --cflags) && \
    VERSION=$(rpm -q --queryformat '%{VERSION}' net-snmp-devel) && \
    mkdir -p /usr/lib64/pkgconfig && \
    printf "prefix=/usr\nexec_prefix=\${prefix}\nlibdir=\${exec_prefix}/lib64\nincludedir=\${prefix}/include\n\nName: netsnmp\nDescription: A collection of libraries for SNMP applications.\nVersion: %s\nLibs: %s\nCflags: %s\n" "$VERSION" "$LIBS" "$CFLAGS" > /usr/lib64/pkgconfig/netsnmp.pc

# Define the path for the virtual environment
ENV VENV_PATH=/opt/venv

# Create the virtual environment using Python 3.13
RUN python3.13 -m venv $VENV_PATH

# Activate the virtual environment
ENV PATH="$VENV_PATH/bin:$PATH"

# Install Python requirements for project and tests inside the virtualenv
COPY requirements.txt /tmp/requirements.txt
COPY python_tests/requirements.txt /tmp/python_tests_requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/python_tests_requirements.txt && \
    rm -f /tmp/requirements.txt /tmp/python_tests_requirements.txt