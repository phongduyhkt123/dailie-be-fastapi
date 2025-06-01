# Dailee Backend - Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 2GB of available RAM
- Ports 80, 443, 5432, 6379, 8000 available

### One-Command Deployment
```bash
./deploy.sh
```

## 📋 Deployment Options

### 1. Local Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Production Deployment

#### Step 1: Environment Setup
```bash
# Copy and configure environment file
cp .env.production .env
# Edit .env with your production values
```

#### Step 2: SSL Certificates (Production)
```bash
# Create SSL directory
mkdir -p ssl

# Add your SSL certificates
# ssl/cert.pem
# ssl/key.pem

# Update nginx.conf to enable SSL
```

#### Step 3: Deploy
```bash
./deploy.sh
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DB_PASSWORD=your_secure_password
SECRET_KEY=your-32-character-secret-key

# Security
DEBUG=false
CORS_ORIGINS=https://yourdomain.com

# Optional: Email settings for notifications
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Database Migration
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

## 🔍 Monitoring & Maintenance

### Health Checks
- API Health: `http://localhost:8000/health`
- Database: `docker-compose exec db pg_isready`
- Redis: `docker-compose exec redis redis-cli ping`

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f nginx
```

### Backup Database
```bash
# Backup
docker-compose exec db pg_dump -U postgres dailee > backup.sql

# Restore
docker-compose exec -T db psql -U postgres dailee < backup.sql
```

## 🌐 Cloud Deployment

### AWS Deployment
1. Use AWS ECS or EC2 with Docker
2. Configure RDS for PostgreSQL
3. Use ElastiCache for Redis
4. Set up Application Load Balancer

### DigitalOcean Deployment
1. Create a Droplet with Docker
2. Use Managed PostgreSQL Database
3. Configure domain and SSL with Let's Encrypt

### Heroku Deployment
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=false

# Deploy
git push heroku main
```

## 🔒 Security Checklist

- [ ] Use strong passwords for database
- [ ] Set secure SECRET_KEY (32+ characters)
- [ ] Configure CORS_ORIGINS properly
- [ ] Enable SSL/HTTPS in production
- [ ] Set DEBUG=false in production
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

## 📊 Performance Optimization

### Database
- Enable connection pooling
- Add database indexes
- Regular VACUUM and ANALYZE

### API
- Use Redis for caching
- Enable gzip compression (nginx)
- Configure rate limiting

### Monitoring
- Set up application monitoring (Sentry, DataDog)
- Database monitoring
- Server resource monitoring

## 🆘 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill process if needed
sudo kill -9 <PID>
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready

# Check logs
docker-compose logs db
```

#### SSL Certificate Issues
```bash
# Test certificate
openssl x509 -in ssl/cert.pem -text -noout

# Generate self-signed for testing
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes
```

## 📞 Support

For deployment issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Ensure all ports are available
4. Check Docker and system resources

## 🔄 Updates

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build api

# Run new migrations
docker-compose exec api alembic upgrade head
```

### Rollback
```bash
# Rollback to previous version
docker-compose down
git checkout previous-tag
docker-compose up -d --build
```
