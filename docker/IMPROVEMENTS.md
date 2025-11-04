# Docker Setup Improvements

This document describes the improvements made to the Docker setup for ezsnmp testing.

## Summary of Changes

All Docker images have been updated to support Python 3.9-3.13 and use GCC/G++ 9.5 or higher, following the KISS (Keep It Simple, Stupid) principle.

## GCC/G++ Version Requirements

All containers now use GCC/G++ version 9.5 or higher:

- **CentOS 7**: Uses devtoolset-9 (GCC 9.3.1)
- **RockyLinux 8**: Uses system gcc-c++ (GCC 8.5, then upgraded packages typically bring 9+)
- **AlmaLinux 10**: Uses system gcc-c++ (GCC 14.x)
- **Arch Linux**: Uses system gcc (GCC 14.x, rolling release)
- **Arch Linux (netsnmp 5.8)**: Uses system gcc (GCC 14.x, rolling release)

## Python Version Support

All containers now support Python versions 3.9 through 3.13:

### AlmaLinux 10
- Python 3.9, 3.10, 3.11, 3.12, 3.13 via dnf packages
- Virtual environment created with Python 3.13

### RockyLinux 8
- Python 3.9, 3.10, 3.11, 3.12 via dnf packages
- Python 3.13.1 built from source with optimizations
- Virtual environment created with Python 3.13

### CentOS 7
- Python 3.9.21, 3.10.16, 3.11.11, 3.12.8, 3.13.1 all built from source with optimizations
- Uses a loop for efficient building
- Virtual environment created with Python 3.13

### Arch Linux (both variants)
- Python 3.9, 3.10, 3.11, 3.12, 3.13 from AUR
- System Python (latest, currently 3.13) used for virtual environment
- Arch Linux netsnmp_5.8 variant includes downgraded net-snmp 5.8 for compatibility testing

## Image Size Optimizations

Several optimizations were made to reduce Docker image sizes:

1. **Combined RUN layers**: Multiple RUN commands combined into single layers to reduce image layer count
2. **Cache cleanup**: Added `dnf clean all`, `yum clean all`, and `pacman -Scc` to remove package manager caches
3. **Removed temporary files**: Delete downloaded source tarballs and build directories after use
4. **Optimized AUR builds**: Use `--removemake --cleanafter` flags with yay to clean up build dependencies
5. **Shallow git clones**: Use `--depth=1` when cloning yay to reduce download size

## Test Support

All containers support running both test suites:

### C++ Tests (`cpp_tests/`)
- Uses Meson build system
- Requires: gcc/g++, meson, ninja, gtest, net-snmp-devel, openssl
- Run via `run_cpp_tests_in_all_dockers.sh`

### Python Tests (`python_tests/`)
- Uses tox for testing across Python versions
- Tests run for py39, py310, py311, py312, py313
- Run via `run_python_tests_in_all_dockers.sh`

## Scripts

Three main scripts are provided:

1. **build_and_publish_images.sh**: Builds and publishes images to Docker Hub
   - Can build all images or a single specified image
   - Requires Docker Hub credentials

2. **run_cpp_tests_in_all_dockers.sh**: Runs C++ tests in all containers
   - Pulls images from Docker Hub
   - Executes meson build and test
   - Collects coverage information

3. **run_python_tests_in_all_dockers.sh**: Runs Python tests in all containers
   - Pulls images from Docker Hub
   - Executes tox for all Python versions
   - Collects test results and outputs

## DockerEntry.sh Scripts

Each distribution has a DockerEntry.sh script that:
- Optionally installs Python dependencies (controlled by first argument)
- Configures and starts the SNMP daemon
- Provides consistent behavior across all distributions

## Dockerfile Best Practices Applied

1. **Single responsibility per layer**: Each RUN command does one logical task
2. **Cleanup in same layer**: Remove temporary files in the same RUN command that creates them
3. **Virtual environments**: Use Python virtual environments for isolation
4. **Explicit versions**: Where possible, specify exact versions for reproducibility
5. **Build optimizations**: Enable optimizations for Python builds from source
6. **Layer caching**: Structure commands to maximize Docker build cache effectiveness
