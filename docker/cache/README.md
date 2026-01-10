# Docker Cache Directory

This directory contains cached source tarballs and packages to avoid repeated downloads during Docker image builds.

## Usage

Before building Docker images, run the download script to populate the cache:

```bash
cd docker/cache
./download_build_cache.sh
```

The script will download all required files if they're not already cached.

To verify the cache is properly set up:

```bash
cd docker/cache
./verify_cache.sh
```

## Cached Files

### Python Source Tarballs
- Python-3.10.16.tgz (~25MB)
- Python-3.11.11.tgz (~26MB)
- Python-3.12.8.tgz (~27MB)
- Python-3.13.7.tgz (~27MB)
- Python-3.14.2.tgz (~27MB)

### OpenSSL (for CentOS7)
- openssl-1.1.1w.tar.gz (~9.5MB)

### Archlinux Packages (for net-snmp 5.7/5.8 compatibility testing)
- net-snmp-5.7.3-1-x86_64.pkg.tar.xz (~1.3MB)
- net-snmp-5.8-1-x86_64.pkg.tar.xz (~1.3MB)
- pcre-8.43-1-x86_64.pkg.tar.xz (~930KB)
- openssl-1.1-1.1.1.w-1-x86_64.pkg.tar.zst (~3.8MB)

**Total cache size: ~150MB**

## Benefits

- **Faster builds**: No repeated downloads across different container builds
- **Offline capability**: Once cached, builds work without internet (for Python sources)
- **Bandwidth savings**: Each tarball is downloaded only once
- **Build reliability**: Reduces dependency on external network availability

## Maintenance

When updating versions in Dockerfiles:

**For Python versions:**
1. Update `PYTHON_*_VERSION` ARGs in Dockerfiles
2. Update `PYTHON_VERSIONS` array in `download_build_cache.sh`

**For OpenSSL:**
1. Update the OpenSSL version in centos7 Dockerfile
2. Update `OPENSSL_VERSION` in `download_build_cache.sh`

**For Archlinux packages:**
1. Update package URLs in archlinux_netsnmp_* Dockerfiles
2. Update `ARCHLINUX_PACKAGES` array in `download_build_cache.sh`

After updating, run the download script to fetch new versions. Old versions can be manually removed from the cache directory if no longer needed.
