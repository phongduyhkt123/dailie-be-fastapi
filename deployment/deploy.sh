#!/bin/bash

# Dailee Backend Deployment Script
# This script helps deploy the Dailee FastAPI backend

set -e

echo "🚀 Starting Dailee Backend Deployment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Create environment file if it doesn't exist
setup_environment() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.production .env
        print_warning "Please update the .env file with your production values before continuing!"
        read -p "Press Enter to continue after updating .env file..."
    else
        print_status "Environment file exists ✓"
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec api alembic upgrade head || {
        print_warning "Migrations failed. This might be expected for first-time deployment."
    }
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build the application
    docker-compose build --no-cache api
    
    # Start all services
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Services are running ✓"
    else
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Wait a bit more for the API to be fully ready
    sleep 5
    
    # Check API health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_status "API health check passed ✓"
    else
        print_warning "API health check failed. The service might still be starting up."
        print_status "You can check the logs with: docker-compose logs api"
    fi
}

# Show deployment info
show_deployment_info() {
    echo -e "\n${BLUE}=== Deployment Complete ===${NC}"
    echo -e "${GREEN}✓ API Server:${NC} http://localhost:8000"
    echo -e "${GREEN}✓ API Documentation:${NC} http://localhost:8000/docs"
    echo -e "${GREEN}✓ Database:${NC} PostgreSQL running on localhost:5432"
    echo -e "${GREEN}✓ Redis:${NC} Running on localhost:6379"
    echo -e "\n${YELLOW}Useful Commands:${NC}"
    echo -e "  • View logs: ${BLUE}docker-compose logs -f${NC}"
    echo -e "  • Stop services: ${BLUE}docker-compose down${NC}"
    echo -e "  • Restart services: ${BLUE}docker-compose restart${NC}"
    echo -e "  • Update application: ${BLUE}docker-compose up -d --build api${NC}"
    echo -e "  • Run migrations: ${BLUE}docker-compose exec api alembic upgrade head${NC}"
    echo -e "  • Access database: ${BLUE}docker-compose exec db psql -U postgres -d dailee${NC}"
}

# Main deployment flow
main() {
    echo -e "${BLUE}🏗️  Dailee Backend Deployment${NC}"
    echo -e "This script will deploy the Dailee FastAPI backend using Docker.\n"
    
    check_docker
    setup_environment
    deploy_services
    health_check
    show_deployment_info
    
    echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
}

# Handle script arguments
case "${1:-}" in
    "clean")
        print_status "Cleaning up containers and volumes..."
        docker-compose down -v
        docker system prune -f
        print_status "Cleanup complete!"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "stop")
        docker-compose down
        print_status "Services stopped!"
        ;;
    "restart")
        docker-compose restart
        print_status "Services restarted!"
        ;;
    *)
        main
        ;;
esac
