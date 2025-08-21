FROM python:3.10

# VARIABLES
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV DEBIAN_FRONTEND=noninteractive

# System deps
RUN apt-get update && apt-get -y install --no-install-recommends \
    vim \
    nano \
    zsh \
    libusb-1.0-0-dev \
    build-essential \
    libgpiod-dev \
    libasound2-dev \
    gstreamer1.0-plugins-bad \
    alsa-utils \
    mpg123 \
    libmpg123-dev \
    unzip \
    ffmpeg \
    git \
    wget \
    htop \
    libopencv-dev \
    kmod \
    sudo \
    xorg \
    openbox \
 && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --upgrade pip \
 && pip install pyserial textual keyboard \
 && pip install "numpy<2.0" torch torchvision \
 && pip install ultralytics opencv-python

# Non-root user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /workspace
