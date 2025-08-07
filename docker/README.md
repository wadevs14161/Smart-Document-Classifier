# Docker Setup for Smart Document Classifier

This directory contains all Docker-related files for running the Smart Document Classifier application.

## Architecture

- **Backend**: FastAPI with Python 3.12.11
- **Frontend**: React with Vite and TypeScript (Node.js 20)
- **Database**: SQLite database file
- **Proxy**: Nginx (production only)

## Quick Start

### Development Environment

```bash
# Navigate to docker directory
cd docker

# Build and start development environment
./docker-helper.sh dev-build
./docker-helper.sh dev-up

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Production Environment

```bash
# Build and start production environment
./docker-helper.sh prod-build
./docker-helper.sh prod-up

# Access the application
# Application: http://localhost
```

## File Structure

```
docker/
├── Dockerfile.backend          # Backend container definition
├── Dockerfile.frontend         # Frontend container definition (multi-stage)
├── docker-compose.yml          # Development orchestration
├── docker-compose.prod.yml     # Production orchestration
├── nginx.conf                  # Nginx configuration for production
├── .env.development            # Development environment variables
├── .env.production             # Production environment variables
├── .dockerignore               # Docker ignore patterns
├── docker-helper.sh            # Management script
└── README.md                   # This file
```

## Available Commands

Use the helper script for easy management:

```bash
./docker-helper.sh [command]
```

### Development Commands
- `dev-build` - Build development containers
- `dev-up` - Start development environment
- `dev-down` - Stop development environment
- `dev-logs` - Show development logs

### Production Commands
- `prod-build` - Build production containers
- `prod-up` - Start production environment
- `prod-down` - Stop production environment
- `prod-logs` - Show production logs

### Utility Commands
- `status` - Show container status
- `clean` - Remove all containers, images, and volumes
- `shell-backend` - Enter backend container shell
- `shell-frontend` - Enter frontend container shell
- `help` - Show help message

## Environment Variables

### Development (.env.development)
- `NODE_ENV=development`
- `VITE_API_BASE_URL=http://localhost:8000/api`
- `DEBUG=true`
- Hot reloading enabled

### Production (.env.production)
- `NODE_ENV=production`
- `VITE_API_BASE_URL=/api`
- `DEBUG=false`
- Optimized builds

## Volumes and Data Persistence

- **Database**: `../documents.db` is mounted to persist SQLite data
- **Uploads**: `../backend/uploads` is mounted for file uploads
- **App Data**: Docker volume `app_data` for application data

## Networking

- **Development**: Both services exposed on host ports (3000, 8000)
- **Production**: Only frontend exposed (port 80), backend accessed via Nginx proxy
- **Internal**: Services communicate via `smart-doc-network`

## Health Checks

The backend container includes health checks that verify the FastAPI application is responding correctly.

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   ./docker-helper.sh clean
   ```

2. **Permission errors**
   ```bash
   sudo chown -R $(whoami) ../backend/uploads
   ```

3. **Database issues**
   - Check if `../documents.db` exists and is accessible
   - Verify database permissions

4. **Frontend not loading**
   - Check if `../frontend/node_modules` exists
   - Verify Vite configuration

### Logs

View logs for debugging:
```bash
./docker-helper.sh dev-logs     # Development
./docker-helper.sh prod-logs    # Production
```

### Container Shell Access

Debug issues by accessing container shells:
```bash
./docker-helper.sh shell-backend   # Python/FastAPI environment
./docker-helper.sh shell-frontend  # Node.js/React environment
```

## Development Workflow

1. Start development environment:
   ```bash
   ./docker-helper.sh dev-up
   ```

2. Make changes to your code (hot reloading enabled)

3. View logs if needed:
   ```bash
   ./docker-helper.sh dev-logs
   ```

4. Stop when done:
   ```bash
   ./docker-helper.sh dev-down
   ```

## Production Deployment

1. Build production containers:
   ```bash
   ./docker-helper.sh prod-build
   ```

2. Start production environment:
   ```bash
   ./docker-helper.sh prod-up
   ```

3. Monitor with logs:
   ```bash
   ./docker-helper.sh prod-logs
   ```

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM recommended
- 10GB+ disk space for ML models
