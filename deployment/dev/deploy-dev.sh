#!/bin/bash

# Dailee Backend Development Deployment Script

set -e

echo "🔧 Starting Dailee Backend Development Deployment..."

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
    if [ ! -f .env.dev ]; then
        print_warning ".env.dev file not found. Creating development environment file..."
        cat > .env.dev << EOL
# Development Environment Configuration
DB_NAME=dailee_dev
DB_USER=postgres
DB_PASSWORD=devpassword
SECRET_KEY=dev-secret-key-not-for-production-use-only
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173,http://127.0.0.1:3000
ENVIRONMENT=development

# Optional: Email settings for development (use mailtrap or similar)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
EOL
        print_status "Created .env.dev file with development defaults"
    fi
}

# Stop existing containers
stop_containers() {
    print_status "Stopping existing development containers..."
    docker-compose -f docker-compose.dev.yml down --remove-orphans || true
}

# Build and start containers
start_containers() {
    print_status "Starting development containers..."
    docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d --build
}

# Run database migrations
run_migrations() {
    print_status "Waiting for database to be ready..."
    sleep 10
    
    print_status "Running database migrations..."
    docker-compose -f docker-compose.dev.yml --env-file .env.dev exec api alembic upgrade head || {
        print_warning "Migrations failed. This might be expected for first run."
    }
}

# Show status
show_status() {
    print_status "Development deployment completed!"
    echo ""
    echo -e "${BLUE}Development Services:${NC}"
    echo "  • API: http://localhost:8001"
    echo "  • API Docs: http://localhost:8001/docs"
    echo "  • Database: localhost:5433"
    echo "  • Redis: localhost:6380"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  • View logs: docker-compose -f docker-compose.dev.yml logs -f"
    echo "  • Stop services: docker-compose -f docker-compose.dev.yml down"
    echo "  • Rebuild API: docker-compose -f docker-compose.dev.yml up -d --build api"
    echo ""
}

# Main execution
main() {
    check_docker
    setup_environment
    stop_containers
    start_containers
    run_migrations
    show_status
}

# Run main function
main "$@"
