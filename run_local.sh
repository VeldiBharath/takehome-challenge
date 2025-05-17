#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Build the Docker image
echo "Building Docker image..."
docker build -t python-executor .

# Run the container
echo "Starting container..."
docker run -p 8080:8080 python-executor

# Note: Press Ctrl+C to stop the container