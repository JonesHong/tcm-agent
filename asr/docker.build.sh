#!/bin/bash

echo "Building Docker image..."
docker build -t whisper_live -f ./docker/Dockerfile.gpu .

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Docker image 'whisper_live' built successfully."
else
  echo "Docker image build failed."
fi
