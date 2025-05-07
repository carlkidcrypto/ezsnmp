# Use Rocky Linux 8 as the base image
FROM rockylinux:8

# Update system
RUN dnf update -y

# Install required tools
RUN dnf install -y findutils

# Install dependencies
COPY dnf-requirements.txt /tmp/dnf-requirements.txt
RUN xargs dnf install -y < /tmp/dnf-requirements.txt && dnf clean all

# Install net-snmp from source
WORKDIR /ezsnmp
RUN wget -O net-snmp.zip https://sourceforge.net/projects/net-snmp/files/net-snmp/5.9.4/net-snmp-5.9.4.zip/download && \
    unzip net-snmp.zip && \
    cd net-snmp-5.9.4 && \
    ./configure --with-defaults --with-mibs=all --disable-manual --without-perl-modules --disable-embedded-perl && \
    make -j$(nproc) && \
    make install && \
    mkdir -p /usr/share/snmp/mibs && \
    cp -r mibs/* /usr/share/snmp/mibs/ && \
    echo "/usr/local/lib" >> /etc/ld.so.conf.d/net-snmp.conf && \
    ldconfig
