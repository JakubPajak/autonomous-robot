# 🚀 Robot Control System with ROS2 and YOLOv5

## 📌 Overview
This project implements an **autonomous robot control system** using **ROS2** (Robot Operating System 2).  
The robot is capable of navigating its environment while detecting and recognizing **traffic signs** using the **YOLOv5** machine learning model.  
The system integrates **motion control, perception, and decision-making** to enable autonomous movement and intelligent interaction with the surroundings.

## 🎯 Features
✅ **Autonomous Navigation** – The robot follows predefined paths or dynamically reacts to detected traffic signs.  
✅ **Traffic Sign Recognition** – Utilizes **YOLOv5**, a state-of-the-art object detection model, to recognize and classify traffic signs in real-time.  
✅ **ROS2-Based Architecture** – Leverages ROS2 for modularity, communication, and scalability.  
✅ **Sensor Integration** – Uses **cameras** for vision-based recognition and additional sensors (e.g., **LiDAR, IMU**) for enhanced navigation.  
✅ **Real-Time Processing** – Optimized inference pipeline ensures efficient processing of video streams for **real-time decision-making**.  

## 🏗️ System Architecture
The project is structured into multiple **ROS2 nodes**:
- 🏎️ **Navigation Node** – Controls the robot's movement and path planning.
- 🎯 **Perception Node** – Processes camera input and runs the YOLOv5 model for sign detection.
- 🤖 **Decision-Making Node** – Interprets detected signs and adjusts robot behavior accordingly.
- 🔗 **Communication Node** – Handles data exchange between different components.

## 📦 Requirements
To run this project, you need the following dependencies:
- 🟢 **ROS2** (Galactic/Humble recommended)
- 🐍 **Python 3.8+**
- 🏆 **YOLOv5** (PyTorch-based model)
- 🎥 **OpenCV** (for image processing)
- ⚡ **TensorRT** (optional for optimized inference)
- 📷 **Camera Module** (e.g., USB or CSI camera)
- 🤖 **Robot Hardware** (such as a mobile platform with motor control)

## 🔧 Installation
```bash
# Set up ROS2
sudo apt update && sudo apt install ros-humble-desktop
source /opt/ros/humble/setup.bash

# Clone the repository
git clone https://github.com/your-repo/robot-control-ros2.git
cd robot-control-ros2

# Install dependencies
pip install -r requirements.txt

# Build and source the workspace
colcon build
source install/setup.bash

# Run the system
ros2 launch robot_control main.launch.py
