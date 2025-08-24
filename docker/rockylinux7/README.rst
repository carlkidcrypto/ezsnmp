=========================
Rocky Linux 7 Dockerfile
=========================

Overview
========
This directory contains the Dockerfile and related resources for building a Docker image based on **Rocky Linux 7**[cite: 6].
The image is designed to contain all the necessary components for testing and development purposes[cite: 7].

Usage
=====

Building the Image
------------------
To build the Docker image, navigate to the `docker/rockylinux8` directory and run the following command[cite: 8]:

.. code-block:: bash

    ./go_docker.sh

This assumes that you have Docker installed and running on your system. The script will build the Docker image using the `Dockerfile` in the current directory[cite: 9]. If you want to clean up any intermediate or dangling Docker images before building, you can use the `--clean` flag[cite: 10]:

.. code-block:: bash

    ./go_docker.sh --clean

The `--clean` flag ensures that your Docker environment is tidy by removing unnecessary images before proceeding with the build[cite: 10].

Running the Container
---------------------
The ./go_docker.sh script will also run the container after building the image[cite: 11]. You can customize the script to pass additional arguments to the `docker run` command if needed[cite: 12]. To run the container interactively, you can use the following command[cite: 13]:

.. code-block:: bash

    docker run -it --rm rocky_linux7_snmp_container /bin/bash

Extending the Image
-------------------
You can extend the base image by modifying the `Dockerfile` to include additional packages, configurations, or scripts. After making changes, rebuild the image using the ./go_docker.sh script[cite: 14].

Directory Structure
===================
The `docker/rockylinux8` folder contains the following files[cite: 15]:

- **Dockerfile**: Defines the instructions for building the Docker image[cite: 15].
- **README.rst**: Documentation for the Docker image.
- **go_docker.sh**: A shell script to automate the build and run process for the Docker image.
- **yum-requirements.txt**: A list of required packages to be installed in the Docker image.
- **docker-compose.yml**: A Docker Compose file for defining and running multi-container Docker applications.
- **DockerEntryPoint.sh**: A script that serves as the entry point for the Docker container, allowing for custom initialization or setup tasks.

Contributing
============
Contributions are welcome! If you encounter issues, have suggestions, or want to add features, feel free to open an issue or submit a pull request on the project's GitHub repository[cite: 20].