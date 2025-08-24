# Use Rocky Linux 8 as the base image
FROM rockylinux:8

# Update system and install essential tools
RUN dnf update -y && \
    dnf install -y findutils dnf-plugins-core

# Install the EPEL repository package
RUN dnf install -y epel-release

# Enable the 'powertools' repository (all lowercase)
RUN dnf config-manager --set-enabled powertools

# Install dependencies from the requirements file AND the newer GCC toolset
COPY dnf-requirements.txt /tmp/dnf-requirements.txt
RUN dnf install -y gcc-toolset-12 && \
    xargs dnf install -y < /tmp/dnf-requirements.txt && \
    dnf clean all

# Install debug symbols for relevant packages
RUN dnf debuginfo-install -y python3 net-snmp-libs

# Manually create the pkg-config file for net-snmp by dynamically
# getting the correct flags and version from the system. This ensures
# that Meson can find the dependency even if PKG_CONFIG_PATH is not set.
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

# Create the virtual environment
RUN python3.9 -m venv $VENV_PATH

# Activate the virtual environment by adding its bin directory to the PATH.
# All subsequent RUN, CMD, and ENTRYPOINT instructions will use this venv.
ENV PATH="$VENV_PATH/bin:$PATH"