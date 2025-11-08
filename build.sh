#!/bin/bash

# Docker Build Script with Git Pull and Timestamp Tags
# File: build.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
IMAGE_NAME="expense-overseer"  # Change this to your image name

print_status "Starting build process..."

# Step 1: Git pull
print_status "Pulling latest changes from git..."
if git pull; then
    print_success "Git pull completed successfully"
else
    print_error "Git pull failed"
    exit 1
fi

# Step 2: Generate build metadata
BUILD_DATE=$(date +%Y%m%d-%H%M)
BUILD_TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Create comprehensive tag
BUILD_TAG="${BUILD_DATE}-${GIT_HASH}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${BUILD_DATE}"

print_status "Build metadata:"
echo "  - Build Date: ${BUILD_DATE}"
echo "  - Git Hash: ${GIT_HASH}"
echo "  - Git Branch: ${GIT_BRANCH}"
echo "  - Full Image Name: ${FULL_IMAGE_NAME}"

# Step 3: Docker build
print_status "Building Docker image..."
if docker build \
    --build-arg BUILD_DATE="${BUILD_TIMESTAMP}" \
    --build-arg BUILD_VERSION="${BUILD_TAG}" \
    --build-arg GIT_HASH="${GIT_HASH}" \
    --build-arg GIT_BRANCH="${GIT_BRANCH}" \
    -t "${FULL_IMAGE_NAME}" \
    -t "${IMAGE_NAME}:latest" \
    .; then
    print_success "Docker build completed successfully"
    print_success "Image tagged as: ${FULL_IMAGE_NAME}"
    print_success "Image tagged as: ${IMAGE_NAME}:latest"
else
    print_error "Docker build failed"
    exit 1
fi

## Optional: Display image info
#print_status "Image information:"
#docker images "${REGISTRY_PREFIX}${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
#
#print_success "Build process completed successfully!"

