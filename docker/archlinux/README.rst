=========================
Arch Linux Dockerfile
=========================

Overview
========
This directory contains the Dockerfile and related resources for building a Docker image based on **Arch Linux**.
The image is designed to contain all the necessary components for testing and development purposes.

Note: DES is disabled in Arch Linux, so the image does not include DES support. As such
unit tests using DES will not pass.

Usage
=====

Building the Image
------------------
To build the Docker image, navigate to the `docker/archlinux` directory and run the following command:

.. code-block:: bash

    ./go_docker.sh

This assumes that you have Docker installed and running on your system. The script will build the Docker image using the `Dockerfile` in the current directory.

If you want to clean up any intermediate or dangling Docker images before building, you can use the `--clean` flag:

.. code-block:: bash

    ./go_docker.sh --clean

The `--clean` flag ensures that your Docker environment is tidy by removing unnecessary images before proceeding with the build.

Running the Container
---------------------
The ./go_docker.sh script will also run the container after building the image. You can customize the script to pass additional arguments to the `docker run` command if needed.
To run the container interactively, you can use the following command:

.. code-block:: bash

    docker run -it --rm archlinux_snmp_container /bin/bash

Extending the Image
-------------------
You can extend the base image by modifying the `Dockerfile` to include additional packages, configurations, or scripts. After making changes, rebuild the image using the ./go_docker.sh script.


Directory Structure
===================
The `docker/archlinux` folder contains the following files:

- **Dockerfile**: Defines the instructions for building the Docker image.
- **README.rst**: Documentation for the Docker image.
- **go_docker.sh**: A shell script to automate the build and run process for the Docker image.
- **dnf-requirements.txt**: A list of required packages to be installed in the Docker image.
- **docker-compose.yml**: A Docker Compose file for defining and running multi-container Docker applications.
- **DockerEntry.sh**: A script that serves as the entry point for the Docker container, allowing for custom initialization or setup tasks.

Contributing
============
Contributions are welcome! If you encounter issues, have suggestions, or want to add features, feel free to open an issue or submit a pull request on the project's GitHub repository.
