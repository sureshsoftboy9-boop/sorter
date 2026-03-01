#!/bin/bash

# PhotoSort Docker Deployment Script
# Makes it easy to deploy and manage PhotoSort in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    print_success "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose is installed"
}

# Start PhotoSort
start_photosort() {
    print_header "Starting PhotoSort"
    docker-compose up -d
    print_success "PhotoSort is running!"
    
    # Get container status
    sleep 2
    if docker ps | grep -q photosort; then
        print_success "Container is healthy"
        
        # Get IP address
        IP=$(hostname -I | awk '{print $1}')
        echo ""
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}🎉 PhotoSort is ready!${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo "📍 Access from this machine:"
        echo "   http://localhost:5000"
        echo ""
        echo "📍 Access from other devices on network:"
        echo "   http://$IP:5000"
        echo ""
        echo "📍 Your IP address: $IP"
        echo ""
    else
        print_error "Container failed to start. Check logs with: docker logs photosort"
        exit 1
    fi
}

# Stop PhotoSort
stop_photosort() {
    print_header "Stopping PhotoSort"
    docker-compose down
    print_success "PhotoSort stopped"
}

# View logs
view_logs() {
    print_header "PhotoSort Logs"
    docker logs -f photosort
}

# Show status
show_status() {
    print_header "PhotoSort Status"
    
    if docker ps | grep -q photosort; then
        print_success "PhotoSort is running"
        echo ""
        docker ps --filter "name=photosort" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_warning "PhotoSort is not running"
    fi
}

# Build image
build_image() {
    print_header "Building Docker Image"
    docker-compose build --no-cache
    print_success "Image built successfully"
}

# Rebuild and restart
rebuild() {
    print_header "Rebuilding and Restarting"
    stop_photosort
    build_image
    start_photosort
}

# Clean up
cleanup() {
    print_header "Cleaning Up"
    docker-compose down -v
    print_success "Cleanup complete"
}

# Usage info
show_usage() {
    echo ""
    print_header "PhotoSort Docker Manager"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start PhotoSort container"
    echo "  stop        - Stop PhotoSort container"
    echo "  status      - Show PhotoSort status"
    echo "  logs        - View PhotoSort logs"
    echo "  build       - Build Docker image"
    echo "  rebuild     - Rebuild image and restart"
    echo "  clean       - Stop and remove everything"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start PhotoSort"
    echo "  $0 logs       # View logs"
    echo "  $0 status     # Check if running"
    echo ""
}

# Main
main() {
    local command=${1:-help}
    
    case $command in
        start)
            check_docker
            check_docker_compose
            start_photosort
            ;;
        stop)
            stop_photosort
            ;;
        status)
            show_status
            ;;
        logs)
            view_logs
            ;;
        build)
            check_docker
            check_docker_compose
            build_image
            ;;
        rebuild)
            check_docker
            check_docker_compose
            rebuild
            ;;
        clean)
            cleanup
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
