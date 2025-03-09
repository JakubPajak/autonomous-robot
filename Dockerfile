ARG ROS_DISTRO=humble

FROM ros:${ROS_DISTRO}-ros-base

# VARIABLES
ARG BUILD_TYPE="RelWithDebInfo"
ARG SIM=0
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install --no-install-recommends \
    vim \
    nano \
    zsh \
    software-properties-common \
    libusb-1.0-0-dev \
    python3-colcon-common-extensions \
    python3-rosdep \
    build-essential \
    gpiod \
    libasound2-dev \
    ros-${ROS_DISTRO}-rclpy \ 
    ros-${ROS_DISTRO}-rviz2 \
    ros-${ROS_DISTRO}-pcl-ros \
    ros-${ROS_DISTRO}-std-msgs \
    ros-${ROS_DISTRO}-cv-bridge \ 
    ros-${ROS_DISTRO}-image-transport \
    ros-${ROS_DISTRO}-image-transport-plugins \
    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
    ros-${ROS_DISTRO}-image-proc \
    ros-${ROS_DISTRO}-rtabmap-slam \ 
    ros-${ROS_DISTRO}-rtabmap \ 
    ros-${ROS_DISTRO}-rtabmap-ros \ 
    ros-${ROS_DISTRO}-depthai-ros \ 
    gstreamer1.0-plugins-bad \
    alsa-utils \
    mpg123 \
    libmpg123-dev \
    unzip \
    ffmpeg \
    git \
    wget \
    htop \
    python3-pip \
    qtbase5-private-dev \
    libopencv-dev \
    kmod \
    kbd \
    ~nros-humble-rqt*

RUN pip install --upgrade pip && \
    pip install pyserial textual keyboard depthai

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

RUN apt update && apt upgrade -y && apt install -y \
    ros-${ROS_DISTRO}-foxglove-bridge \
    ros-${ROS_DISTRO}-bond \
    ros-${ROS_DISTRO}-control-msgs \
    ros-${ROS_DISTRO}-sensor-msgs \
    ros-${ROS_DISTRO}-controller-manager-msgs \
    ros-${ROS_DISTRO}-joy \
    ros-${ROS_DISTRO}-image-transport-plugins \
    ros-${ROS_DISTRO}-gazebo-ros-pkgs \ 
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    ros-${ROS_DISTRO}-joint-state-publisher*

# For creating a non root user in the container
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt update \
    && apt install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /workspace
