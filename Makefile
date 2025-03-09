# Makefile for building ROS2 AGV project
SHELL := /bin/bash
PROJECT_NAME := ROS2_AMR
BUILD_DIR := build
INSTALL_DIR := install
LOG_DIR := log

# Msg packages (need to be built and sourced first)
MSG_PCKG := interfaces

# Targets
.PHONY: all clean

# Default target
all: clean build

# Build target
build:
	@bash build_workspace.bash
	
# Clean target
clean:
	@echo "Cleaning $(PROJECT_NAME) build files..."
	@rm -rf $(BUILD_DIR) $(LOG_DIR) $(INSTALL_DIR)
