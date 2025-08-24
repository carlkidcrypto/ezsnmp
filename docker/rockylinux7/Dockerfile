# Use CentOS 7 as the base image
FROM centos:7

# Update system and install essential tools
RUN yum update -y && \
    yum install -y yum-utils findutils

# Install the EPEL repository package [cite: 1]
RUN yum install -y epel-release

# Install the IUS repository to get access to Python 3.9
RUN yum install -y https://repo.ius.io/ius-release-el7.rpm

# Install dependencies from the requirements file [cite: 1]
COPY yum-requirements.txt /tmp/yum-requirements.txt
RUN yum install -y $(cat /tmp/yum-requirements.txt) && yum clean all

# Install debug symbols for relevant packages [cite: 1]
RUN yum-config-manager --enable base-debuginfo ius && \
    debuginfo-install -y python39 net-snmp-libs

# Manually create the pkg-config file for net-snmp by dynamically
# getting the correct flags and version from the system. [cite: 2, 3, 4]
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

# Define the path for the virtual environment [cite: 5]
ENV VENV_PATH=/opt/venv

# Create the virtual environment using python3.9 [cite: 5]
RUN python3.9 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH. [cite: 5]
ENV PATH="$VENV_PATH/bin:$PATH"