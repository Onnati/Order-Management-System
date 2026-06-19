#!/usr/bin/env bash
# Build and push the backend image to Docker Hub.
#
# Usage:
#   ./scripts/publish-backend-dockerhub.sh YOUR_DOCKERHUB_USERNAME
#
# Example:
#   ./scripts/publish-backend-dockerhub.sh johndoe
#
# Resulting image link:
#   https://hub.docker.com/r/johndoe/order-management-api
#   docker pull johndoe/order-management-api:latest

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <dockerhub-username> [tag]"
  echo "Example: $0 johndoe latest"
  exit 1
fi

DOCKERHUB_USER="$1"
TAG="${2:-latest}"
IMAGE_NAME="order-management-api"
FULL_IMAGE="${DOCKERHUB_USER}/${IMAGE_NAME}:${TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "==> Logging in to Docker Hub (enter your Docker Hub password/token)"
docker login

echo "==> Building backend image: ${FULL_IMAGE}"
docker build -t "${FULL_IMAGE}" "${PROJECT_ROOT}/backend"

echo "==> Pushing to Docker Hub..."
docker push "${FULL_IMAGE}"

echo ""
echo "Done! Your public Docker Hub links:"
echo "  Hub page:  https://hub.docker.com/r/${DOCKERHUB_USER}/${IMAGE_NAME}"
echo "  Pull cmd:  docker pull ${FULL_IMAGE}"
echo "  Image ref: ${FULL_IMAGE}"
