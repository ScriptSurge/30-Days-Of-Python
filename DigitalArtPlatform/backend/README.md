# Backend

Python FastAPI backend for the Digital Art Platform.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **PostgreSQL Database**: Robust relational database with full-text search
- **SQLAlchemy ORM**: Type-safe database operations
- **Alembic Migrations**: Version-controlled database schema
- **JWT Authentication**: Secure token-based authentication
- **Celery Background Jobs**: Async image processing and external API calls
- **Redis Caching**: Fast in-memory caching layer
- **Pydantic Validation**: Request/response validation with type hints
- **Comprehensive Testing**: Unit and integration tests with pytest

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Redis 7 or higher
- Docker (optional, for containerized development)

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 3. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode (with Gunicorn)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 6. Access the Application

- API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc

## Docker Deployment

```bash
# Build image
docker build -t digitalart-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379 \
  -e SECRET_KEY=your-secret-key \
  digitalart-backend

# Or use Docker Compose
docker-compose up -d
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/
│   └── env.py
├── app/
│   ├── main.py           # Application entry point
│   ├── config.py         # Configuration management
│   ├── dependencies.py   # Dependency injection
│   │
│   ├── api/              # API endpoints
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   │
│   ├── core/             # Core functionality
│   │   ├── security.py   # Authentication & authorization
│   │   ├── config.py     # Settings
│   │   └── events.py     # Startup/shutdown events
│   │
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── artwork.py
│   │   └── ...
│   │
│   ├── schemas/          # Pydantic schemas (DTOs)
│   │   ├── user.py
│   │   ├── artwork.py
│   │   └── ...
│   │
│   ├── services/         # Business logic
│   │   ├── auth_service.py
│   │   ├── artwork_service.py
│   │   └── ...
│   │
│   ├── repositories/     # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   └── ...
│   │
│   ├── integrations/     # External APIs
│   │   ├── museums/
│   │   ├── storage/
│   │   └── ai/
│   │
│   ├── workers/          # Celery background tasks
│   │   ├── celery_app.py
│   │   └── tasks/
│   │
│   ├── db/               # Database utilities
│   │   ├── base.py
│   │   └── session.py
│   │
│   └── tests/            # Test suite
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── .env.example
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/unit/test_user_service.py

# Run specific test
pytest app/tests/unit/test_user_service.py::test_create_user
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add artwork table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# Show current version
alembic current
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
pylint app/
```

### Background Workers

```bash
# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Start Celery beat (scheduled tasks)
celery -A app.workers.celery_app beat --loglevel=info

# Monitor Celery
celery -A app.workers.celery_app flower
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and revoke refresh token

### Users
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user
- `GET /api/v1/users/me/stats` - Get user statistics

### Artworks
- `GET /api/v1/artworks` - List artworks (with filters)
- `GET /api/v1/artworks/{id}` - Get artwork details
- `POST /api/v1/artworks` - Upload artwork
- `PATCH /api/v1/artworks/{id}` - Update artwork
- `DELETE /api/v1/artworks/{id}` - Delete artwork
- `POST /api/v1/artworks/{id}/favorite` - Favorite artwork
- `DELETE /api/v1/artworks/{id}/favorite` - Unfavorite artwork

### Collections
- `GET /api/v1/collections` - List collections
- `GET /api/v1/collections/{id}` - Get collection details
- `POST /api/v1/collections` - Create collection
- `PATCH /api/v1/collections/{id}` - Update collection
- `DELETE /api/v1/collections/{id}` - Delete collection

See [API Documentation](../documentation/API_SPECIFICATION.md) for complete reference.

## Configuration

Key environment variables:

```bash
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/digitalart

# Redis
REDIS_URL=redis://localhost:6379

# Storage
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=digitalart-uploads
AWS_REGION=us-east-1

# Authentication
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# External APIs
OPENAI_API_KEY=your-openai-key
```

## Deployment

See [Deployment Guide](../documentation/DEPLOYMENT.md) for production deployment instructions.

## Contributing

See [Coding Standards](../documentation/CODING_STANDARDS.md) for code style guidelines.

## License

MIT License - see [LICENSE](../LICENSE) file for details.
