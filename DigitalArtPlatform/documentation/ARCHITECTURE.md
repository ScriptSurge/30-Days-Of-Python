# System Architecture

## Overview

The Digital Art Platform is designed as a distributed system with multiple client applications connecting to a central backend API. The architecture follows microservices principles with clear separation of concerns, allowing for independent scaling and deployment of components.

## Design Principles

### 1. **SaaS-First Architecture**
- Multi-tenant support from day one
- Subscription and billing-ready data model
- User organization and home management
- Role-based access control (RBAC)
- Audit logging and analytics

### 2. **Scalability**
- Horizontal scaling for API servers
- CDN integration for artwork delivery
- Database read replicas
- Caching layers (Redis)
- Background job processing (Celery)
- Support for 100,000+ artworks per user

### 3. **Performance**
- Lazy loading and pagination
- Image optimization and thumbnail generation
- Aggressive caching strategy
- Offline-first client applications
- Background synchronization

### 4. **Security**
- JWT-based authentication
- OAuth 2.0 support
- Encrypted credentials storage
- Rate limiting
- HTTPS everywhere
- CORS policies

### 5. **Maintainability**
- Clean architecture with dependency injection
- Comprehensive test coverage (unit, integration, e2e)
- API versioning
- Structured logging
- Monitoring and observability

### 6. **User Experience**
- Fast response times (<100ms for cached content)
- Progressive enhancement
- Graceful degradation
- Intuitive UX following platform conventions

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   iOS App    │ Web Dashboard│  Samsung TV  │  Raspberry Pi      │
│   (SwiftUI)  │  (React/TS)  │   (Tizen)    │  (Python/Electron) │
└──────┬───────┴──────┬───────┴──────┬───────┴─────────┬──────────┘
       │              │              │                 │
       └──────────────┴──────────────┴─────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │    Load Balancer        │
              │    (nginx/ALB)          │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    API Gateway          │
              │    (FastAPI)            │
              └────────────┬────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Auth       │  │   Artwork    │  │  Background  │
│   Service    │  │   Service    │  │    Jobs      │
│              │  │              │  │  (Celery)    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       └─────────────────┼──────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
  ┌───────────┐   ┌───────────┐   ┌──────────┐
  │PostgreSQL │   │   Redis   │   │   S3/    │
  │ Database  │   │   Cache   │   │  Object  │
  │           │   │           │   │  Storage │
  └───────────┘   └───────────┘   └──────────┘
         │
         ▼
  ┌───────────┐
  │ElasticSearch│
  │  (Search)   │
  └─────────────┘
```

## Component Architecture

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── api/                       # API layer
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── artworks.py
│   │   │   │   ├── collections.py
│   │   │   │   ├── playlists.py
│   │   │   │   ├── devices.py
│   │   │   │   ├── schedules.py
│   │   │   │   └── search.py
│   │   │   └── router.py
│   │   └── deps.py                # API dependencies
│   │
│   ├── core/                      # Core functionality
│   │   ├── security.py            # Authentication & authorization
│   │   ├── config.py              # Settings management
│   │   └── events.py              # Startup/shutdown events
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── artwork.py
│   │   ├── collection.py
│   │   ├── playlist.py
│   │   ├── device.py
│   │   ├── schedule.py
│   │   └── ...
│   │
│   ├── schemas/                   # Pydantic schemas (DTOs)
│   │   ├── user.py
│   │   ├── artwork.py
│   │   ├── collection.py
│   │   └── ...
│   │
│   ├── services/                  # Business logic layer
│   │   ├── auth_service.py
│   │   ├── artwork_service.py
│   │   ├── collection_service.py
│   │   ├── image_service.py       # Image processing
│   │   ├── metadata_service.py    # Metadata extraction
│   │   ├── search_service.py
│   │   ├── ai_service.py          # AI features
│   │   ├── integration_service.py # External APIs
│   │   └── ...
│   │
│   ├── repositories/              # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── artwork_repository.py
│   │   └── ...
│   │
│   ├── integrations/              # External service integrations
│   │   ├── museums/
│   │   │   ├── met.py
│   │   │   ├── rijksmuseum.py
│   │   │   └── ...
│   │   ├── storage/
│   │   │   ├── google_drive.py
│   │   │   ├── dropbox.py
│   │   │   └── s3.py
│   │   └── ai/
│   │       ├── openai_client.py
│   │       └── stable_diffusion.py
│   │
│   ├── workers/                   # Background tasks
│   │   ├── celery_app.py
│   │   ├── tasks/
│   │   │   ├── image_processing.py
│   │   │   ├── metadata_extraction.py
│   │   │   ├── sync_tasks.py
│   │   │   └── ai_tasks.py
│   │   └── ...
│   │
│   ├── db/                        # Database utilities
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/            # Alembic migrations
│   │
│   └── tests/                     # Test suite
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
├── alembic/                       # Database migrations
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── pytest.ini
```

### Architecture Patterns

#### 1. Layered Architecture

```
┌──────────────────────────────────┐
│         API Layer (FastAPI)      │  ← HTTP endpoints, validation
├──────────────────────────────────┤
│      Service Layer (Business)    │  ← Business logic, orchestration
├──────────────────────────────────┤
│    Repository Layer (Data)       │  ← Data access, queries
├──────────────────────────────────┤
│     Database Layer (PostgreSQL)  │  ← Persistence
└──────────────────────────────────┘
```

#### 2. Dependency Injection

```python
# Example: Injecting dependencies
@router.get("/artworks/{artwork_id}")
async def get_artwork(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    artwork_service: ArtworkService = Depends(get_artwork_service),
    db: Session = Depends(get_db)
):
    return await artwork_service.get_artwork(artwork_id, current_user)
```

#### 3. Repository Pattern

```python
class ArtworkRepository(BaseRepository[Artwork]):
    def get_by_artist(self, artist_id: int) -> List[Artwork]:
        return self.db.query(Artwork).filter(
            Artwork.artist_id == artist_id
        ).all()
    
    def search(self, query: str, filters: dict) -> List[Artwork]:
        # Complex search logic
        pass
```

#### 4. Service Pattern

```python
class ArtworkService:
    def __init__(
        self,
        artwork_repo: ArtworkRepository,
        image_service: ImageService,
        metadata_service: MetadataService
    ):
        self.artwork_repo = artwork_repo
        self.image_service = image_service
        self.metadata_service = metadata_service
    
    async def create_artwork(self, data: ArtworkCreate) -> Artwork:
        # Process image
        image_data = await self.image_service.process(data.image_url)
        
        # Extract metadata
        metadata = await self.metadata_service.extract(image_data)
        
        # Save to database
        artwork = await self.artwork_repo.create({
            **data.dict(),
            **metadata
        })
        
        # Trigger background jobs
        generate_thumbnails.delay(artwork.id)
        
        return artwork
```

## Data Flow

### 1. User Uploads Artwork

```
User (iOS) → API → Image Service → S3 Storage
                ↓
         Metadata Service
                ↓
         Artwork Repository → PostgreSQL
                ↓
         Background Job → Thumbnail Generation
                ↓
         Cache (Redis) ← Artwork Service
```

### 2. Browse Collections

```
User (Web) → API → Cache (Redis) → Return cached data
                      ↓ (Cache miss)
                 Artwork Service
                      ↓
                 Artwork Repository
                      ↓
                 PostgreSQL
                      ↓
                 Store in Cache
```

### 3. Smart TV Display

```
Samsung TV → API (Get Next Artwork)
                ↓
         Schedule Service (Check schedule rules)
                ↓
         Recommendation Service (AI)
                ↓
         Artwork Service
                ↓
         CDN URL → Return to TV
```

## Scaling Strategy

### Horizontal Scaling

1. **API Servers**: Multiple FastAPI instances behind load balancer
2. **Database**: PostgreSQL with read replicas
3. **Cache**: Redis cluster
4. **Background Workers**: Multiple Celery workers
5. **Storage**: S3 or compatible object storage with CDN

### Vertical Scaling

1. **Database**: Increase PostgreSQL resources for complex queries
2. **Image Processing**: GPU instances for AI features
3. **Search**: ElasticSearch cluster for advanced search

### Optimization Strategies

1. **Caching**
   - Redis for frequently accessed data (collections, popular artworks)
   - CDN for image delivery
   - Browser caching for static assets

2. **Database Optimization**
   - Proper indexing strategy
   - Query optimization
   - Connection pooling
   - Prepared statements

3. **Image Optimization**
   - WebP format for modern browsers
   - Multiple resolutions (thumbnail, preview, full)
   - Lazy loading
   - Progressive JPEG

4. **API Optimization**
   - Pagination for list endpoints
   - Field selection (sparse fieldsets)
   - Batch operations
   - Rate limiting

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. API validates with database
   ↓
3. Generate JWT access token (15 min) + refresh token (7 days)
   ↓
4. Return tokens to client
   ↓
5. Client includes access token in Authorization header
   ↓
6. API validates JWT on each request
   ↓
7. Access token expires → Use refresh token to get new access token
```

### Authorization

- **Role-Based Access Control (RBAC)**
  - Admin: Full system access
  - User: Access to own content
  - Viewer: Read-only access
  - Device: Limited access for TV/display devices

### Security Measures

1. **Transport Security**
   - HTTPS/TLS everywhere
   - Certificate pinning for mobile apps
   
2. **Authentication**
   - JWT tokens with short expiration
   - Refresh token rotation
   - OAuth 2.0 for third-party integrations
   
3. **Authorization**
   - Role-based access control
   - Resource-level permissions
   - API key management for devices
   
4. **Data Protection**
   - Encrypted passwords (bcrypt)
   - Encrypted API keys and tokens
   - PII encryption at rest
   
5. **API Security**
   - Rate limiting (per user, per IP)
   - Request size limits
   - SQL injection prevention (parameterized queries)
   - XSS prevention
   - CSRF protection

## Monitoring & Observability

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Centralized log aggregation (ELK stack or similar)
- Request ID tracing

### Metrics
- Application metrics (request rate, response time, error rate)
- System metrics (CPU, memory, disk, network)
- Business metrics (active users, artworks viewed, API calls)
- Custom metrics via Prometheus

### Tracing
- Distributed tracing with OpenTelemetry
- Request flow visualization
- Performance bottleneck identification

### Alerting
- Error rate thresholds
- Response time degradation
- Resource utilization
- Security events

## Deployment Architecture

### Development Environment
- Docker Compose
- Local PostgreSQL
- Local Redis
- Local S3 (MinIO)

### Staging Environment
- Kubernetes cluster
- Managed PostgreSQL (AWS RDS / Google Cloud SQL)
- Managed Redis (ElastiCache / Cloud Memorystore)
- S3 / Google Cloud Storage
- HTTPS with Let's Encrypt

### Production Environment
- Multi-region Kubernetes deployment
- PostgreSQL with replication
- Redis cluster
- Global CDN (CloudFlare / CloudFront)
- Auto-scaling policies
- Database backups (daily + point-in-time recovery)
- Monitoring and alerting

## Technology Decisions

### Why FastAPI?
- ✅ Modern, fast (async/await)
- ✅ Automatic API documentation (OpenAPI/Swagger)
- ✅ Type hints and validation (Pydantic)
- ✅ Easy to test
- ✅ Great performance
- ✅ Growing ecosystem

### Why PostgreSQL?
- ✅ Mature, reliable
- ✅ ACID compliance
- ✅ JSON support (JSONB)
- ✅ Full-text search
- ✅ Rich extension ecosystem
- ✅ Excellent performance
- ✅ Open source

### Why SQLAlchemy?
- ✅ Mature ORM
- ✅ Supports both sync and async
- ✅ Migration support (Alembic)
- ✅ Type-safe queries
- ✅ Connection pooling

### Why Redis?
- ✅ Fast in-memory cache
- ✅ Pub/sub support
- ✅ Session storage
- ✅ Rate limiting
- ✅ Job queues (with Celery)

### Why Celery?
- ✅ Distributed task queue
- ✅ Scheduling support
- ✅ Retry logic
- ✅ Monitoring tools
- ✅ Battle-tested

## Future Considerations

### Microservices Evolution

As the platform grows, consider splitting into microservices:

1. **Auth Service**: Authentication and authorization
2. **Artwork Service**: Artwork CRUD and metadata
3. **Media Service**: Image processing and storage
4. **Search Service**: Advanced search and recommendations
5. **Integration Service**: External API integrations
6. **Analytics Service**: Usage analytics and insights

### Event-Driven Architecture

Consider adopting event-driven patterns:
- Event sourcing for audit trails
- CQRS for read/write separation
- Message queues (RabbitMQ / Kafka)
- Webhooks for real-time updates

### GraphQL API

Add GraphQL alongside REST for:
- Flexible client queries
- Reduced over-fetching
- Real-time subscriptions
- Better mobile performance

---

**Last Updated**: 2026-07-26  
**Architecture Version**: 1.0  
**Next Review**: Q4 2026
