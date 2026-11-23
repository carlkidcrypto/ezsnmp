FROM python:3.13-slim-trixie

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    file \
    g++ \
    gcc \
    git \
    libssl-dev \
    make \
    perl \
    pkg-config \
    snmpd \
    swig \
    valgrind \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel pytest

RUN curl --proto '=https' --proto-redir '=https' -fsSL \
    https://raw.githubusercontent.com/python/cpython/main/Misc/valgrind-python.supp \
    -o /tmp/valgrind-python.supp

WORKDIR /workspace
