#!/bin/bash

# Dailee Backend Production Deployment Script

set -e

echo "🚀 Starting Dailee Backend Production Deployment..."

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

# Check production environment file
check_environment() {
    if [ ! -f .env.prod ]; then
        print_error ".env.prod file not found!"
        print_error "Please create .env.prod file with production configuration."
        print_error "Use .env.prod.template as reference."
        exit 1
    fi
    
    # Check required environment variables
    source .env.prod
    
    if [ -z "$DB_PASSWORD" ]; then
        print_error "DB_PASSWORD is not set in .env.prod"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ] || [ ${#SECRET_KEY} -lt 32 ]; then
        print_error "SECRET_KEY is not set or too short in .env.prod (minimum 32 characters)"
        exit 1
    fi
    
    if [ -z "$CORS_ORIGINS" ]; then
        print_error "CORS_ORIGINS is not set in .env.prod"
        exit 1
    fi
    
    print_status "Environment configuration validated ✓"
}

# Check SSL certificates
check_ssl() {
    if [ ! -d "ssl" ]; then
        print_warning "SSL directory not found. Creating..."
        mkdir -p ssl
    fi
    
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_warning "SSL certificates not found."
        print_warning "For production, please add your SSL certificates:"
        print_warning "  • ssl/cert.pem"
        print_warning "  • ssl/key.pem"
        print_warning ""
        print_warning "For testing, you can generate self-signed certificates:"
        print_warning "openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes"
        
        read -p "Continue without SSL? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_status "SSL certificates found ✓"
    fi
}

# Create logs directory
setup_logs() {
    mkdir -p logs/nginx
    print_status "Logs directory created ✓"
}

# Stop existing containers
stop_containers() {
    print_status "Stopping existing production containers..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
}

# Build and start containers
start_containers() {
    print_status "Starting production containers..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
}

# Run database migrations
run_migrations() {
    print_status "Waiting for database to be ready..."
    sleep 15
    
    print_status "Running database migrations..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod exec api alembic upgrade head
}

# Show status
show_status() {
    print_status "Production deployment completed!"
    echo ""
    echo -e "${BLUE}Production Services:${NC}"
    echo "  • API: https://your-domain.com (or http://localhost if no SSL)"
    echo "  • API Docs: https://your-domain.com/docs"
    echo "  • Health Check: https://your-domain.com/health"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  • View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  • Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "  • Backup DB: docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres dailee > backup.sql"
    echo ""
    echo -e "${YELLOW}Security Reminders:${NC}"
    echo "  • Ensure your domain points to this server"
    echo "  • Configure firewall to only allow necessary ports"
    echo "  • Regularly update and monitor your deployment"
    echo "  • Set up automated backups"
}

# Main execution
main() {
    check_docker
    check_environment
    check_ssl
    setup_logs
    stop_containers
    start_containers
    run_migrations
    show_status
}

# Run main function
main "$@"
