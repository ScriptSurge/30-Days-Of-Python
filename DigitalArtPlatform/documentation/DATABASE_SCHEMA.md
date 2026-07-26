# Database Schema

## Overview

The Digital Art Platform uses PostgreSQL as its primary database with a normalized relational schema designed for scalability, data integrity, and multi-tenancy support.

## Design Principles

1. **Normalization**: 3NF (Third Normal Form) for data integrity
2. **Multi-tenancy**: Support for multiple users and organizations
3. **Soft Deletes**: Use `deleted_at` timestamp instead of hard deletes
4. **Audit Trail**: Track created/updated timestamps and user IDs
5. **Indexing**: Strategic indexes for performance
6. **JSON Support**: JSONB fields for flexible metadata
7. **Full-Text Search**: PostgreSQL full-text search capabilities
8. **Foreign Keys**: Enforce referential integrity

## Core Entities

### 1. Users & Authentication

#### users
Primary user table with authentication details.

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    
    -- Account status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Subscription (for SaaS)
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    subscription_expires_at TIMESTAMPTZ,
    
    -- Preferences
    preferences JSONB DEFAULT '{}',
    
    -- OAuth
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    
    CONSTRAINT email_lowercase CHECK (email = LOWER(email))
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_uuid ON users(uuid);
CREATE INDEX idx_users_oauth ON users(oauth_provider, oauth_id) WHERE oauth_provider IS NOT NULL;
CREATE INDEX idx_users_subscription ON users(subscription_tier, subscription_status);
```

#### refresh_tokens
Store refresh tokens for JWT authentication.

```sql
CREATE TABLE refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    device_info JSONB,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE revoked_at IS NULL;
```

### 2. Organizations & Homes

#### organizations
Support for team/family accounts (SaaS feature).

```sql
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    owner_id BIGINT NOT NULL REFERENCES users(id),
    
    subscription_tier VARCHAR(50) DEFAULT 'free',
    settings JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_organizations_owner ON organizations(owner_id);
CREATE INDEX idx_organizations_slug ON organizations(slug) WHERE deleted_at IS NULL;
```

#### organization_members
Many-to-many relationship between users and organizations.

```sql
CREATE TABLE organization_members (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- owner, admin, member, viewer
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(organization_id, user_id)
);

CREATE INDEX idx_org_members_org ON organization_members(organization_id);
CREATE INDEX idx_org_members_user ON organization_members(user_id);
```

#### homes
Physical locations with display devices (supports multiple homes per user).

```sql
CREATE TABLE homes (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    address TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    settings JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_homes_user ON homes(user_id);
CREATE INDEX idx_homes_org ON homes(organization_id);
```

### 3. Artworks

#### artists
Artist information from various sources.

```sql
CREATE TABLE artists (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    name VARCHAR(255) NOT NULL,
    biography TEXT,
    birth_year INTEGER,
    death_year INTEGER,
    nationality VARCHAR(100),
    
    -- External IDs for deduplication
    external_ids JSONB DEFAULT '{}',
    
    -- Stats
    artwork_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_artists_name ON artists(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_artists_external_ids ON artists USING GIN(external_ids);
```

#### artworks
Core artwork table.

```sql
CREATE TABLE artworks (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- Ownership (NULL for public domain)
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    organization_id BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Basic info
    title VARCHAR(500) NOT NULL,
    description TEXT,
    artist_id BIGINT REFERENCES artists(id) ON DELETE SET NULL,
    artist_name VARCHAR(255), -- Denormalized for performance
    year INTEGER,
    
    -- Source
    source VARCHAR(50) NOT NULL, -- 'met_museum', 'user_upload', 'unsplash', 'ai_generated', etc.
    source_id VARCHAR(255),
    source_url TEXT,
    license VARCHAR(100),
    
    -- Image URLs
    original_url TEXT NOT NULL,
    thumbnail_url TEXT,
    preview_url TEXT,
    high_res_url TEXT,
    
    -- Storage
    storage_provider VARCHAR(50), -- 's3', 'google_drive', 'dropbox', etc.
    storage_path TEXT,
    file_size BIGINT,
    
    -- Image metadata
    width INTEGER,
    height INTEGER,
    aspect_ratio DECIMAL(10, 4),
    orientation VARCHAR(20), -- 'landscape', 'portrait', 'square'
    format VARCHAR(20), -- 'jpg', 'png', 'webp'
    
    -- Visual properties
    dominant_colors JSONB, -- Array of hex colors
    average_color VARCHAR(7), -- Single hex color
    brightness DECIMAL(3, 2), -- 0.0 to 1.0
    
    -- Classification
    medium VARCHAR(100), -- 'painting', 'photograph', 'sculpture', etc.
    style VARCHAR(100), -- 'impressionism', 'modern', 'abstract', etc.
    subject_matter TEXT[],
    tags TEXT[],
    
    -- Location
    museum VARCHAR(255),
    museum_department VARCHAR(255),
    object_location VARCHAR(255),
    country VARCHAR(100),
    city VARCHAR(100),
    
    -- AI-generated metadata
    ai_description TEXT,
    ai_tags TEXT[],
    ai_embedding VECTOR(1536), -- For similarity search (requires pgvector extension)
    
    -- Stats
    view_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    
    -- Flags
    is_public BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_mature_content BOOLEAN DEFAULT FALSE,
    
    -- Search
    search_vector TSVECTOR,
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    CONSTRAINT valid_year CHECK (year IS NULL OR (year >= -5000 AND year <= 2100)),
    CONSTRAINT valid_dimensions CHECK (width > 0 AND height > 0)
);

-- Indexes
CREATE INDEX idx_artworks_user ON artworks(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_artworks_org ON artworks(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_artworks_artist ON artworks(artist_id);
CREATE INDEX idx_artworks_source ON artworks(source, source_id);
CREATE INDEX idx_artworks_orientation ON artworks(orientation);
CREATE INDEX idx_artworks_year ON artworks(year) WHERE year IS NOT NULL;
CREATE INDEX idx_artworks_tags ON artworks USING GIN(tags);
CREATE INDEX idx_artworks_public ON artworks(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_artworks_featured ON artworks(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_artworks_search ON artworks USING GIN(search_vector);
CREATE INDEX idx_artworks_colors ON artworks USING GIN(dominant_colors);

-- Full-text search trigger
CREATE TRIGGER artworks_search_vector_update
BEFORE INSERT OR UPDATE ON artworks
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description, tags, artist_name);
```

### 4. Collections & Playlists

#### collections
Curated groups of artworks.

```sql
CREATE TABLE collections (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- Ownership
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    organization_id BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cover_artwork_id BIGINT REFERENCES artworks(id) ON DELETE SET NULL,
    
    -- Type
    collection_type VARCHAR(50) DEFAULT 'custom', -- 'custom', 'smart', 'system', 'seasonal'
    
    -- Smart collection rules (JSONB for flexibility)
    smart_rules JSONB,
    
    -- Display
    sort_order VARCHAR(50) DEFAULT 'manual', -- 'manual', 'date_added', 'chronological', 'random'
    is_public BOOLEAN DEFAULT FALSE,
    is_system BOOLEAN DEFAULT FALSE, -- For built-in collections like "Favorites"
    
    -- Stats
    artwork_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_collections_user ON collections(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_collections_org ON collections(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_collections_type ON collections(collection_type);
CREATE INDEX idx_collections_public ON collections(is_public) WHERE is_public = TRUE;
```

#### collection_artworks
Many-to-many relationship between collections and artworks.

```sql
CREATE TABLE collection_artworks (
    id BIGSERIAL PRIMARY KEY,
    collection_id BIGINT NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    artwork_id BIGINT NOT NULL REFERENCES artworks(id) ON DELETE CASCADE,
    
    position INTEGER, -- For manual ordering
    
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    added_by_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    
    UNIQUE(collection_id, artwork_id)
);

CREATE INDEX idx_collection_artworks_collection ON collection_artworks(collection_id, position);
CREATE INDEX idx_collection_artworks_artwork ON collection_artworks(artwork_id);
```

#### playlists
Sequential display lists (like Spotify playlists).

```sql
CREATE TABLE playlists (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    home_id BIGINT REFERENCES homes(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cover_artwork_id BIGINT REFERENCES artworks(id) ON DELETE SET NULL,
    
    -- Playback settings
    shuffle_mode BOOLEAN DEFAULT FALSE,
    repeat_mode VARCHAR(20) DEFAULT 'off', -- 'off', 'all', 'one'
    interval_seconds INTEGER DEFAULT 3600, -- How long to show each artwork
    
    -- Stats
    artwork_count INTEGER DEFAULT 0,
    play_count INTEGER DEFAULT 0,
    
    is_public BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_playlists_user ON playlists(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_playlists_home ON playlists(home_id);
```

#### playlist_items
Ordered artworks in playlists.

```sql
CREATE TABLE playlist_items (
    id BIGSERIAL PRIMARY KEY,
    playlist_id BIGINT NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    artwork_id BIGINT NOT NULL REFERENCES artworks(id) ON DELETE CASCADE,
    
    position INTEGER NOT NULL,
    
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(playlist_id, artwork_id),
    UNIQUE(playlist_id, position)
);

CREATE INDEX idx_playlist_items_playlist ON playlist_items(playlist_id, position);
CREATE INDEX idx_playlist_items_artwork ON playlist_items(artwork_id);
```

### 5. User Interactions

#### favorites
User favorites (many-to-many).

```sql
CREATE TABLE favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    artwork_id BIGINT NOT NULL REFERENCES artworks(id) ON DELETE CASCADE,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id, artwork_id)
);

CREATE INDEX idx_favorites_user ON favorites(user_id, created_at DESC);
CREATE INDEX idx_favorites_artwork ON favorites(artwork_id);
```

#### artwork_views
Track artwork views for analytics and recommendations.

```sql
CREATE TABLE artwork_views (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    artwork_id BIGINT NOT NULL REFERENCES artworks(id) ON DELETE CASCADE,
    device_id BIGINT REFERENCES devices(id) ON DELETE SET NULL,
    
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_seconds INTEGER, -- How long was it displayed
    
    -- Context
    source VARCHAR(50), -- 'browse', 'playlist', 'recommendation', 'shuffle'
    session_id UUID
);

CREATE INDEX idx_artwork_views_user ON artwork_views(user_id, viewed_at DESC);
CREATE INDEX idx_artwork_views_artwork ON artwork_views(artwork_id, viewed_at DESC);
CREATE INDEX idx_artwork_views_device ON artwork_views(device_id);
CREATE INDEX idx_artwork_views_session ON artwork_views(session_id);

-- Partition by month for performance
-- CREATE TABLE artwork_views_y2026m07 PARTITION OF artwork_views
-- FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
```

### 6. Devices

#### devices
Registered display devices (TVs, Raspberry Pis, etc.).

```sql
CREATE TABLE devices (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    home_id BIGINT REFERENCES homes(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    device_type VARCHAR(50) NOT NULL, -- 'samsung_tv', 'raspberry_pi', 'lg_webos', 'chromecast', etc.
    model VARCHAR(100),
    
    -- Authentication
    api_key_hash VARCHAR(255) NOT NULL UNIQUE,
    
    -- Capabilities
    max_width INTEGER,
    max_height INTEGER,
    supported_formats TEXT[],
    
    -- Display settings
    display_mode VARCHAR(50) DEFAULT 'fit', -- 'fit', 'fill', 'stretch'
    brightness DECIMAL(3, 2) DEFAULT 1.0,
    
    -- Network
    ip_address INET,
    mac_address MACADDR,
    
    -- Status
    is_online BOOLEAN DEFAULT FALSE,
    last_seen_at TIMESTAMPTZ,
    
    -- Stats
    total_views INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_devices_user ON devices(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_devices_home ON devices(home_id);
CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_devices_online ON devices(is_online) WHERE is_online = TRUE;
```

### 7. Schedules

#### schedules
Smart scheduling rules for artwork display.

```sql
CREATE TABLE schedules (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id BIGINT REFERENCES devices(id) ON DELETE CASCADE,
    home_id BIGINT REFERENCES homes(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    is_enabled BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0, -- Higher priority schedules override lower ones
    
    -- Time rules (JSONB for flexibility)
    time_rules JSONB NOT NULL,
    -- Example: {
    --   "days_of_week": [1, 2, 3, 4, 5], // Monday-Friday
    --   "time_range": {"start": "09:00", "end": "17:00"},
    --   "date_range": {"start": "2026-01-01", "end": "2026-12-31"},
    --   "holidays": ["christmas", "new_year"],
    --   "seasons": ["winter"]
    -- }
    
    -- What to display
    content_type VARCHAR(50) NOT NULL, -- 'collection', 'playlist', 'tag', 'ai_recommendation'
    content_id BIGINT, -- Reference to collection_id or playlist_id
    content_filters JSONB, -- Additional filters
    
    -- Display settings
    interval_seconds INTEGER DEFAULT 3600,
    shuffle_mode BOOLEAN DEFAULT FALSE,
    transition_effect VARCHAR(50) DEFAULT 'fade',
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_schedules_user ON schedules(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_schedules_device ON schedules(device_id);
CREATE INDEX idx_schedules_enabled ON schedules(is_enabled, priority) WHERE is_enabled = TRUE;
```

### 8. External Integrations

#### external_connections
Store OAuth tokens and connection info for external services.

```sql
CREATE TABLE external_connections (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    provider VARCHAR(50) NOT NULL, -- 'google_drive', 'dropbox', 'onedrive', etc.
    
    -- OAuth tokens (encrypted)
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMPTZ,
    
    -- Connection metadata
    external_user_id VARCHAR(255),
    external_username VARCHAR(255),
    scopes TEXT[],
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id, provider)
);

CREATE INDEX idx_external_connections_user ON external_connections(user_id);
CREATE INDEX idx_external_connections_provider ON external_connections(provider);
```

#### sync_jobs
Track background synchronization jobs.

```sql
CREATE TABLE sync_jobs (
    id BIGSERIAL PRIMARY KEY,
    
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connection_id BIGINT REFERENCES external_connections(id) ON DELETE CASCADE,
    
    job_type VARCHAR(50) NOT NULL, -- 'import', 'sync', 'export'
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    
    -- Progress
    total_items INTEGER,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    
    -- Results
    error_message TEXT,
    result_data JSONB,
    
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sync_jobs_user ON sync_jobs(user_id, created_at DESC);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status) WHERE status IN ('pending', 'running');
```

### 9. AI & Recommendations

#### ai_generations
Track AI-generated content.

```sql
CREATE TABLE ai_generations (
    id BIGSERIAL PRIMARY KEY,
    
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    artwork_id BIGINT REFERENCES artworks(id) ON DELETE SET NULL,
    
    generation_type VARCHAR(50) NOT NULL, -- 'image', 'description', 'tags', 'recommendation'
    provider VARCHAR(50) NOT NULL, -- 'openai', 'stable_diffusion', 'flux'
    model VARCHAR(100),
    
    prompt TEXT,
    parameters JSONB,
    
    result JSONB,
    cost_credits DECIMAL(10, 4),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_generations_user ON ai_generations(user_id, created_at DESC);
CREATE INDEX idx_ai_generations_type ON ai_generations(generation_type);
```

#### recommendations
Store pre-computed recommendations.

```sql
CREATE TABLE recommendations (
    id BIGSERIAL PRIMARY KEY,
    
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    artwork_id BIGINT NOT NULL REFERENCES artworks(id) ON DELETE CASCADE,
    
    recommendation_type VARCHAR(50) NOT NULL, -- 'similar', 'based_on_history', 'trending', 'seasonal'
    score DECIMAL(5, 4) NOT NULL, -- 0.0 to 1.0
    
    reason TEXT,
    metadata JSONB,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    
    UNIQUE(user_id, artwork_id, recommendation_type)
);

CREATE INDEX idx_recommendations_user ON recommendations(user_id, score DESC);
CREATE INDEX idx_recommendations_expires ON recommendations(expires_at) WHERE expires_at IS NOT NULL;
```

### 10. Analytics

#### analytics_events
Track user events for analytics.

```sql
CREATE TABLE analytics_events (
    id BIGSERIAL PRIMARY KEY,
    
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    device_id BIGINT REFERENCES devices(id) ON DELETE SET NULL,
    session_id UUID,
    
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analytics_events_user ON analytics_events(user_id, created_at DESC);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type, created_at DESC);
CREATE INDEX idx_analytics_events_session ON analytics_events(session_id);

-- Partition by month
-- CREATE TABLE analytics_events_y2026m07 PARTITION OF analytics_events
-- FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
```

## Relationships Diagram

```
users ────────────────────┬─────────────────┬──────────────────┐
  │                        │                 │                  │
  │                        │                 │                  │
  ├─ organizations         ├─ homes          ├─ artworks       ├─ devices
  │    │                   │    │            │    │             │
  │    └─ org_members      │    └─ devices   │    ├─ artists   └─ schedules
  │                        │                 │    │
  ├─ collections           ├─ playlists      │    ├─ collection_artworks
  │    │                   │    │            │    │
  │    └─ collection_      │    └─ playlist_ │    ├─ favorites
  │         artworks       │         items   │    │
  │                        │                 │    └─ artwork_views
  │                        │                 │
  ├─ favorites             ├─ external_      └─ recommendations
  │                        │    connections
  │                        │         │
  └─ analytics_events      └─ sync_jobs
```

## Data Volume Estimates

| Table | Estimated Rows (Year 1) | Growth Rate |
|-------|------------------------|-------------|
| users | 10,000 | Medium |
| artworks | 1,000,000 | High |
| collections | 50,000 | Medium |
| collection_artworks | 5,000,000 | High |
| playlists | 20,000 | Medium |
| favorites | 500,000 | High |
| artwork_views | 10,000,000 | Very High |
| devices | 15,000 | Low |
| analytics_events | 50,000,000 | Very High |

## Performance Optimization

### Indexing Strategy

1. **Primary Keys**: All tables use BIGSERIAL for scalability
2. **Foreign Keys**: Indexed automatically
3. **Lookup Fields**: Email, UUID, slugs
4. **Filter Fields**: Status flags, timestamps
5. **Full-Text Search**: GIN indexes on TSVECTOR columns
6. **JSONB Fields**: GIN indexes for complex queries
7. **Composite Indexes**: User + timestamp for common queries

### Query Optimization

1. **Denormalization**: artist_name in artworks table
2. **Counters**: artwork_count, favorite_count (updated via triggers)
3. **Materialized Views**: For complex analytics queries
4. **Partitioning**: Time-series tables (views, events) by month
5. **Soft Deletes**: Use indexes with WHERE deleted_at IS NULL

### Caching Strategy

1. **Popular artworks**: Redis cache (1 hour TTL)
2. **User collections**: Redis cache (15 min TTL)
3. **Search results**: Redis cache (5 min TTL)
4. **User preferences**: Redis cache (session lifetime)

## Migration Strategy

### Versioning
- Use Alembic for schema migrations
- Sequential version numbers
- Descriptive migration names
- Both upgrade and downgrade functions

### Zero-Downtime Migrations
1. Additive changes first (new columns, tables)
2. Update application code to support both schemas
3. Deploy application
4. Remove old columns/tables in subsequent migration

### Data Migrations
- Separate data migrations from schema migrations
- Use background jobs for large data transformations
- Implement in batches with progress tracking

## Backup & Recovery

### Backup Strategy
- **Daily**: Full database backup
- **Continuous**: Write-ahead log (WAL) archiving for point-in-time recovery
- **Retention**: 30 days daily, 12 months monthly
- **Testing**: Monthly restore tests

### Disaster Recovery
- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 5 minutes
- **Multi-region replication**: For production
- **Automated failover**: Using PostgreSQL replication

## Security

### Data Protection
1. **Encryption at Rest**: Database-level encryption
2. **Encryption in Transit**: SSL/TLS connections only
3. **PII Encryption**: Additional encryption for sensitive fields
4. **Password Hashing**: bcrypt with cost factor 12
5. **Token Encryption**: AES-256 for OAuth tokens

### Access Control
1. **Principle of Least Privilege**: Application DB user has minimal permissions
2. **Read Replicas**: Separate credentials for read-only access
3. **Admin Access**: Requires MFA and audit logging
4. **Connection Limits**: Per-user connection pooling

## Monitoring

### Metrics to Track
- Query performance (slow query log)
- Connection pool usage
- Table sizes and growth rates
- Index usage statistics
- Replication lag
- Cache hit ratios

### Alerts
- Slow queries (> 1 second)
- High connection count (> 80% of max)
- Replication lag (> 10 seconds)
- Disk space (< 20% free)
- Failed queries (> 1% error rate)

---

**Schema Version**: 1.0  
**Last Updated**: 2026-07-26  
**Database**: PostgreSQL 15+
