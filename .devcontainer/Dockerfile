FROM ros:noetic-ros-core-focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    lsb-release \
    locales \
    python3-pip \
    python3-rosdep \
    python3-catkin-tools \
    python3-rosinstall \
    python3-rosinstall-generator \
    python3-wstool \
    libboost-all-dev \
    libssl-dev \
    nano \
    iputils-ping \
    net-tools \
    x11-apps \
 && rm -rf /var/lib/apt/lists/*

# Try to update rosdep (may fail inside some CI environments)
RUN rosdep update || true

SHELL ["/bin/bash", "-lc"]

# Create a catkin workspace that will be populated from the mounted repository
RUN mkdir -p /workspace/catkin_ws/src
WORKDIR /workspace/catkin_ws

# Keep image small: no heavy additional packages by default. Users can install extras in the container terminal.

CMD ["bash"]
