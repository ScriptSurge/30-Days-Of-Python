# Deployment Guide

## Overview

This guide covers deploying the Digital Art Platform to various environments, from local development to production cloud deployments.

## Table of Contents

1. [Development Environment](#development-environment)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Variables](#environment-variables)
5. [Database Management](#database-management)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling](#scaling)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

---

## Development Environment

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Local Setup

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/digital-art-platform.git
cd digital-art-platform
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Web Dashboard Setup
```bash
cd web-dashboard

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

#### 4. Access Applications
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Web Dashboard: http://localhost:5173

---

## Docker Deployment

### Quick Start with Docker Compose

#### Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

#### Services Included
- **backend**: FastAPI application
- **postgres**: PostgreSQL database
- **redis**: Redis cache
- **celery-worker**: Background task processor
- **celery-beat**: Scheduled tasks
- **nginx**: Reverse proxy (production only)

### Docker Compose Files

#### `docker-compose.yml` (Development)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: digitalart_postgres
    environment:
      POSTGRES_DB: digitalart
      POSTGRES_USER: digitalart
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U digitalart"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: digitalart_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: digitalart_backend
    environment:
      - DATABASE_URL=postgresql://digitalart:${DB_PASSWORD:-changeme}@postgres:5432/digitalart
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=development
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: digitalart_celery_worker
    environment:
      - DATABASE_URL=postgresql://digitalart:${DB_PASSWORD:-changeme}@postgres:5432/digitalart
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend:/app
      - backend_uploads:/app/uploads
    depends_on:
      - postgres
      - redis
      - backend
    command: celery -A app.workers.celery_app worker --loglevel=info

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: digitalart_celery_beat
    environment:
      - DATABASE_URL=postgresql://digitalart:${DB_PASSWORD:-changeme}@postgres:5432/digitalart
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
      - backend
    command: celery -A app.workers.celery_app beat --loglevel=info

volumes:
  postgres_data:
  redis_data:
  backend_uploads:
```

#### `docker-compose.prod.yml` (Production)
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: digitalart_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_files:/var/www/static
    depends_on:
      - backend
      - web
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
      - SENTRY_DSN=${SENTRY_DSN}
    expose:
      - "8000"
    volumes:
      - backend_uploads:/app/uploads
    restart: unless-stopped
    command: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

  web:
    build:
      context: ./web-dashboard
      dockerfile: Dockerfile.prod
    expose:
      - "80"
    restart: unless-stopped

volumes:
  static_files:
  backend_uploads:
```

### Backend Dockerfile

#### `backend/Dockerfile` (Development)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `backend/Dockerfile.prod` (Production)
```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run with gunicorn
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Web Dashboard Dockerfile

#### `web-dashboard/Dockerfile.prod`
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

---

## Production Deployment

### Cloud Platform Options

#### 1. AWS (Recommended)
**Services Used:**
- **ECS/EKS**: Container orchestration
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed Redis
- **S3**: Object storage
- **CloudFront**: CDN
- **Route 53**: DNS
- **ALB**: Load balancing
- **CloudWatch**: Monitoring

#### 2. Google Cloud Platform
**Services Used:**
- **Cloud Run or GKE**: Container hosting
- **Cloud SQL**: PostgreSQL
- **Memorystore**: Redis
- **Cloud Storage**: Object storage
- **Cloud CDN**: Content delivery
- **Cloud Load Balancing**: Load balancing

#### 3. DigitalOcean (Budget-Friendly)
**Services Used:**
- **App Platform or Kubernetes**: Container hosting
- **Managed PostgreSQL**: Database
- **Managed Redis**: Cache
- **Spaces**: Object storage
- **CDN**: Content delivery

### Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (EKS, GKE, or self-hosted)
- kubectl configured
- Helm 3 installed

#### Deploy with Helm

```bash
# Add repository
helm repo add digitalart https://charts.digitalartplatform.com
helm repo update

# Install
helm install digitalart digitalart/digitalart-platform \
  --set backend.image.tag=v1.0.0 \
  --set web.image.tag=v1.0.0 \
  --set postgresql.enabled=false \
  --set externalDatabase.host=your-db-host \
  --set externalDatabase.password=your-db-password \
  --set redis.enabled=false \
  --set externalRedis.host=your-redis-host
```

#### Kubernetes Manifests

**`k8s/backend-deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digitalart-backend
  labels:
    app: digitalart
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digitalart
      component: backend
  template:
    metadata:
      labels:
        app: digitalart
        component: backend
    spec:
      containers:
      - name: backend
        image: digitalart/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: digitalart-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: digitalart-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: digitalart-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: digitalart-backend
spec:
  selector:
    app: digitalart
    component: backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

---

## Environment Variables

### Backend Environment Variables

```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key-here
API_VERSION=v1

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://host:6379
REDIS_PASSWORD=your-redis-password

# Storage
STORAGE_TYPE=s3  # s3, gcs, or local
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
CDN_URL=https://cdn.yourdomain.com

# Authentication
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM=noreply@yourdomain.com

# External APIs
OPENAI_API_KEY=your-openai-key
MET_MUSEUM_API_KEY=your-met-api-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# Celery
CELERY_BROKER_URL=redis://host:6379/0
CELERY_RESULT_BACKEND=redis://host:6379/0

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Web Dashboard Environment Variables

```bash
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
VITE_WS_URL=wss://api.yourdomain.com/ws
VITE_SENTRY_DSN=your-sentry-dsn
VITE_ENVIRONMENT=production
```

---

## Database Management

### Migrations

#### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "Add artwork table"
```

#### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123

# Show current version
alembic current

# Show migration history
alembic history
```

### Backup

#### Automated Backups (PostgreSQL)
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="digitalart_${TIMESTAMP}.sql.gz"

# Create backup
pg_dump -h ${DB_HOST} -U ${DB_USER} -d digitalart | gzip > "${BACKUP_DIR}/${FILENAME}"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/${FILENAME}" s3://your-backup-bucket/postgres/

# Keep only last 30 days locally
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

# S3 lifecycle policy will handle cloud retention
```

#### Restore from Backup
```bash
# Download from S3
aws s3 cp s3://your-backup-bucket/postgres/digitalart_20260726_010000.sql.gz .

# Restore
gunzip digitalart_20260726_010000.sql.gz
psql -h ${DB_HOST} -U ${DB_USER} -d digitalart < digitalart_20260726_010000.sql
```

---

## Monitoring & Logging

### Application Monitoring

#### Sentry (Error Tracking)
```python
# backend/app/core/config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )
```

#### Prometheus Metrics
```python
# backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)
```

### Logging

#### Structured Logging
```python
# backend/app/core/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data)
```

### Health Checks

```python
# backend/app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.cache import get_redis

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    health = {
        "status": "ok",
        "checks": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["checks"]["database"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    # Check Redis
    try:
        redis = get_redis()
        redis.ping()
        health["checks"]["redis"] = "ok"
    except Exception as e:
        health["checks"]["redis"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    return health
```

---

## Security

### SSL/TLS Configuration

#### Let's Encrypt with Certbot
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (added to cron automatically)
sudo certbot renew --dry-run
```

### Nginx Security Headers

```nginx
# nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https:; img-src 'self' https: data:; script-src 'self' 'unsafe-inline';" always;

    # Other configurations...
}
```

### Database Security

- Use SSL for database connections
- Rotate credentials regularly
- Use IAM authentication (AWS RDS)
- Enable encryption at rest
- Implement connection pooling limits

---

## Scaling

### Horizontal Scaling

#### Backend API
```bash
# Increase replicas in Kubernetes
kubectl scale deployment digitalart-backend --replicas=5

# Or with Helm
helm upgrade digitalart digitalart/digitalart-platform \
  --set backend.replicaCount=5
```

#### Auto-scaling (Kubernetes HPA)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: digitalart-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: digitalart-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Scaling

#### Read Replicas
```python
# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Write database
write_engine = create_engine(settings.DATABASE_URL_WRITE)
WriteSession = sessionmaker(bind=write_engine)

# Read replicas
read_engine = create_engine(settings.DATABASE_URL_READ)
ReadSession = sessionmaker(bind=read_engine)

def get_write_db():
    db = WriteSession()
    try:
        yield db
    finally:
        db.close()

def get_read_db():
    db = ReadSession()
    try:
        yield db
    finally:
        db.close()
```

---

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
psql -h your-db-host -U your-db-user -d digitalart

# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < now() - interval '1 hour';
```

#### Redis Connection Issues
```bash
# Test Redis connection
redis-cli -h your-redis-host ping

# Check memory usage
redis-cli -h your-redis-host info memory

# Flush cache if needed
redis-cli -h your-redis-host FLUSHALL
```

#### High CPU Usage
- Check slow queries in PostgreSQL
- Review Celery task performance
- Check for infinite loops in code
- Review image processing jobs

#### High Memory Usage
- Check for memory leaks with profiler
- Review image processing (reduce resolution)
- Limit concurrent Celery workers
- Increase swap space temporarily

---

**Last Updated**: 2026-07-26  
**Version**: 1.0
