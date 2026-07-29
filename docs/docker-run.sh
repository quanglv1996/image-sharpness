#!/bin/bash

# Docker build and run helper script for Image Sharpness Analyzer
# Usage: ./docker-run.sh [command]
# Commands: build, up, down, logs, shell, clean

set -e

CONTAINER_NAME="image-sharpness-app"
IMAGE_NAME="image-sharpness:latest"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo_error "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo_error "Docker Compose is not installed"
    exit 1
fi

# Default command
COMMAND=${1:-up}

case $COMMAND in
    build)
        echo_info "Building Docker image..."
        docker-compose build
        echo_info "Build complete!"
        ;;
    up)
        echo_info "Starting container..."
        docker-compose up -d
        echo_info "Container started!"
        echo_info "Access application at: http://localhost:5000"
        ;;
    down)
        echo_info "Stopping container..."
        docker-compose down
        echo_info "Container stopped!"
        ;;
    restart)
        echo_info "Restarting container..."
        docker-compose restart
        echo_info "Container restarted!"
        ;;
    logs)
        echo_info "Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    shell)
        echo_info "Opening shell in container..."
        docker exec -it $CONTAINER_NAME /bin/bash
        ;;
    status)
        echo_info "Checking container status..."
        docker-compose ps
        ;;
    clean)
        echo_warn "Removing container and image..."
        docker-compose down
        docker rmi $IMAGE_NAME || true
        echo_info "Cleaned up!"
        ;;
    rebuild)
        echo_info "Rebuilding everything..."
        docker-compose down
        docker-compose up --build -d
        echo_info "Rebuild complete!"
        echo_info "Access application at: http://localhost:5000"
        ;;
    *)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  build     - Build Docker image"
        echo "  up        - Start container (default)"
        echo "  down      - Stop container"
        echo "  restart   - Restart container"
        echo "  logs      - View container logs"
        echo "  shell     - Open shell in container"
        echo "  status    - Show container status"
        echo "  clean     - Remove container and image"
        echo "  rebuild   - Clean, rebuild and start"
        exit 1
        ;;
esac
