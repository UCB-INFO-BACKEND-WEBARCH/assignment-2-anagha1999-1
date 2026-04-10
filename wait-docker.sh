#!/bin/bash
echo "Waiting for Docker daemon..."
for i in $(seq 1 30); do
  docker info >/dev/null 2>&1 && echo "Docker is ready!" && exit 0
  echo "Attempt $i - waiting..."
  sleep 3
done
echo "Docker failed to start"
exit 1
