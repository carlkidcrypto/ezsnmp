# Use Rocky Linux 8 as the base image
FROM rockylinux:8

# Update package manager and install dependencies
RUN dnf update -y && \
    dnf install -y \
    wget \
    unzip \
    file \
    make \
    python3.9 \
    python39-devel \
    python3-pip \
    gcc-c++  && \
    dnf clean all

# Install net-snmp from source
WORKDIR /ezsnmp
RUN wget -O net-snmp.zip https://sourceforge.net/projects/net-snmp/files/net-snmp/5.9.4/net-snmp-5.9.4.zip/download && \
    unzip net-snmp.zip && \
    cd net-snmp-5.9.4 && \
    ./configure --with-defaults --with-mibs=all --disable-manual --without-perl-modules --disable-embedded-perl && \
    make -j$(nproc) && \
    make install && \
    mkdir -p /usr/share/snmp/mibs && \
    cp -r mibs/* /usr/share/snmp/mibs/