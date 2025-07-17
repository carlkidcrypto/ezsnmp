# Use AlmaLinux 10-kitten as the base image
FROM almalinux:10-kitten

# Update system
RUN dnf update -y

# Install required tools
RUN dnf install -y findutils

# Install dependencies
COPY dnf-requirements.txt /tmp/dnf-requirements.txt
RUN xargs dnf install -y < /tmp/dnf-requirements.txt && dnf clean all
