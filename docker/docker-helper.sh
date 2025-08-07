#!/bin/bash

# Docker Helper Script for Smart Document Classifier
# This script helps manage the Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to docker directory
cd "$SCRIPT_DIR"

print_usage() {
    echo -e "${BLUE}Smart Document Classifier - Docker Helper${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  dev-build     Build development containers"
    echo "  dev-up        Start development environment"
    echo "  dev-down      Stop development environment"
    echo "  dev-logs      Show development logs"
    echo "  prod-build    Build production containers"
    echo "  prod-up       Start production environment"
    echo "  prod-down     Stop production environment"
    echo "  prod-logs     Show production logs"
    echo "  clean         Remove all containers, images, and volumes"
    echo "  status        Show container status"
    echo "  shell-backend Enter backend container shell"
    echo "  shell-frontend Enter frontend container shell"
    echo "  help          Show this help message"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed or not in PATH${NC}"
        exit 1
    fi
}

case "$1" in
    "dev-build")
        echo -e "${BLUE}🔨 Building development containers...${NC}"
        docker-compose build
        echo -e "${GREEN}✅ Development containers built successfully${NC}"
        ;;
        
    "dev-up")
        echo -e "${BLUE}🚀 Starting development environment...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✅ Development environment started${NC}"
        echo -e "${YELLOW}📱 Frontend: http://localhost:3000${NC}"
        echo -e "${YELLOW}🔧 Backend API: http://localhost:8000${NC}"
        ;;
        
    "dev-down")
        echo -e "${BLUE}🛑 Stopping development environment...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Development environment stopped${NC}"
        ;;
        
    "dev-logs")
        echo -e "${BLUE}📋 Showing development logs...${NC}"
        docker-compose logs -f
        ;;
        
    "prod-build")
        echo -e "${BLUE}🔨 Building production containers...${NC}"
        docker-compose -f docker-compose.prod.yml build
        echo -e "${GREEN}✅ Production containers built successfully${NC}"
        ;;
        
    "prod-up")
        echo -e "${BLUE}🚀 Starting production environment...${NC}"
        docker-compose -f docker-compose.prod.yml up -d
        echo -e "${GREEN}✅ Production environment started${NC}"
        echo -e "${YELLOW}🌐 Application: http://localhost${NC}"
        ;;
        
    "prod-down")
        echo -e "${BLUE}🛑 Stopping production environment...${NC}"
        docker-compose -f docker-compose.prod.yml down
        echo -e "${GREEN}✅ Production environment stopped${NC}"
        ;;
        
    "prod-logs")
        echo -e "${BLUE}📋 Showing production logs...${NC}"
        docker-compose -f docker-compose.prod.yml logs -f
        ;;
        
    "clean")
        echo -e "${YELLOW}⚠️  This will remove all containers, images, and volumes. Are you sure? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${BLUE}🧹 Cleaning up Docker resources...${NC}"
            docker-compose down -v --remove-orphans 2>/dev/null || true
            docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
            docker system prune -af --volumes
            echo -e "${GREEN}✅ Cleanup completed${NC}"
        else
            echo -e "${YELLOW}❌ Cleanup cancelled${NC}"
        fi
        ;;
        
    "status")
        echo -e "${BLUE}📊 Container Status:${NC}"
        docker ps -a --filter "name=smart-doc"
        echo ""
        echo -e "${BLUE}🔗 Network Status:${NC}"
        docker network ls --filter "name=smart-doc"
        ;;
        
    "shell-backend")
        echo -e "${BLUE}🐚 Entering backend container shell...${NC}"
        docker exec -it smart-doc-backend /bin/bash
        ;;
        
    "shell-frontend")
        echo -e "${BLUE}🐚 Entering frontend container shell...${NC}"
        docker exec -it smart-doc-frontend /bin/sh
        ;;
        
    "help"|"--help"|"-h"|"")
        print_usage
        ;;
        
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac