# REST API Specification

## Overview

The Digital Art Platform API is a RESTful API built with FastAPI, following OpenAPI 3.0 specifications. The API is versioned, well-documented, and designed for both web and mobile clients.

## Base URL

```
Development:  http://localhost:8000/api/v1
Staging:      https://staging-api.digitalart.platform/api/v1
Production:   https://api.digitalart.platform/api/v1
```

## API Principles

### 1. REST Conventions
- **Resource-oriented** URLs
- **HTTP methods** for operations (GET, POST, PUT, PATCH, DELETE)
- **HTTP status codes** for response states
- **JSON** for request/response bodies
- **ISO 8601** for timestamps
- **Pagination** for list endpoints
- **Filtering, sorting, and searching** via query parameters

### 2. Versioning
- URL-based versioning (`/api/v1/`, `/api/v2/`)
- Backward compatibility within major versions
- Deprecation warnings in headers before removal

### 3. Authentication
- JWT Bearer tokens in `Authorization` header
- OAuth 2.0 for third-party integrations
- API keys for device authentication

### 4. Rate Limiting
- **Authenticated users**: 1000 requests/hour
- **Anonymous users**: 100 requests/hour
- Rate limit info in response headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

### 5. Error Handling
Consistent error response format:
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "status_code": 404,
  "timestamp": "2026-07-26T02:23:00Z",
  "request_id": "req_abc123xyz",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": false,
  "created_at": "2026-07-26T02:23:00Z"
}
```

### POST /auth/login
Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### POST /auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### POST /auth/logout
Revoke refresh token.

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `204 No Content`

### POST /auth/reset-password
Request password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset email sent"
}
```

## User Endpoints

### GET /users/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "avatar_url": "https://cdn.example.com/avatars/1.jpg",
  "subscription_tier": "premium",
  "subscription_status": "active",
  "preferences": {
    "theme": "dark",
    "notifications_enabled": true
  },
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-07-26T02:23:00Z"
}
```

### PATCH /users/me
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "first_name": "Jane",
  "preferences": {
    "theme": "light"
  }
}
```

**Response:** `200 OK` (returns updated user object)

### GET /users/me/stats
Get user statistics.

**Response:** `200 OK`
```json
{
  "total_artworks": 1234,
  "total_collections": 45,
  "total_playlists": 12,
  "total_favorites": 567,
  "total_views": 8900,
  "storage_used_bytes": 5368709120
}
```

## Artwork Endpoints

### GET /artworks
List artworks with filtering, sorting, and pagination.

**Query Parameters:**
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)
- `sort` (string, default: "created_at", options: "created_at", "title", "year", "views")
- `order` (string, default: "desc", options: "asc", "desc")
- `artist_id` (integer)
- `source` (string)
- `orientation` (string: "landscape", "portrait", "square")
- `year_min` (integer)
- `year_max` (integer)
- `tags` (comma-separated strings)
- `search` (string, full-text search)
- `is_public` (boolean)
- `color` (hex color for similarity search)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "uuid": "art_123abc",
      "title": "Starry Night",
      "description": "A famous painting by Vincent van Gogh...",
      "artist": {
        "id": 1,
        "name": "Vincent van Gogh"
      },
      "year": 1889,
      "source": "met_museum",
      "thumbnail_url": "https://cdn.example.com/thumbnails/1.jpg",
      "preview_url": "https://cdn.example.com/previews/1.jpg",
      "width": 2560,
      "height": 1920,
      "orientation": "landscape",
      "dominant_colors": ["#1e3a8a", "#fbbf24", "#1f2937"],
      "tags": ["impressionism", "night", "stars"],
      "is_public": true,
      "view_count": 1234,
      "favorite_count": 567,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "total": 1234,
  "page": 1,
  "page_size": 20,
  "total_pages": 62
}
```

### GET /artworks/{id}
Get single artwork details.

**Response:** `200 OK`
```json
{
  "id": 1,
  "uuid": "art_123abc",
  "title": "Starry Night",
  "description": "A famous painting by Vincent van Gogh depicting...",
  "artist": {
    "id": 1,
    "uuid": "artist_456def",
    "name": "Vincent van Gogh",
    "birth_year": 1853,
    "death_year": 1890,
    "nationality": "Dutch"
  },
  "year": 1889,
  "source": "met_museum",
  "source_url": "https://www.metmuseum.org/art/collection/...",
  "license": "public_domain",
  "original_url": "https://cdn.example.com/originals/1.jpg",
  "thumbnail_url": "https://cdn.example.com/thumbnails/1.jpg",
  "preview_url": "https://cdn.example.com/previews/1.jpg",
  "high_res_url": "https://cdn.example.com/high_res/1.jpg",
  "width": 2560,
  "height": 1920,
  "aspect_ratio": 1.3333,
  "orientation": "landscape",
  "format": "jpg",
  "file_size": 5242880,
  "dominant_colors": ["#1e3a8a", "#fbbf24", "#1f2937"],
  "average_color": "#3b4f7a",
  "medium": "painting",
  "style": "impressionism",
  "tags": ["impressionism", "night", "stars", "landscape"],
  "museum": "Metropolitan Museum of Art",
  "country": "USA",
  "city": "New York",
  "is_public": true,
  "is_favorite": false,
  "view_count": 1234,
  "favorite_count": 567,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-07-20T14:22:00Z"
}
```

### POST /artworks
Upload new artwork.

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request:**
```
title: "My Photography"
description: "Sunset at the beach"
tags: ["sunset", "beach", "photography"]
year: 2026
is_public: true
image: <binary file>
```

**Response:** `201 Created` (returns artwork object)

### PATCH /artworks/{id}
Update artwork metadata.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "title": "Updated Title",
  "tags": ["new", "tags"],
  "is_public": false
}
```

**Response:** `200 OK` (returns updated artwork object)

### DELETE /artworks/{id}
Delete artwork (soft delete).

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

### GET /artworks/{id}/similar
Get similar artworks using AI.

**Query Parameters:**
- `limit` (integer, default: 10, max: 50)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "artwork": { /* artwork object */ },
      "similarity_score": 0.95,
      "reason": "Similar color palette and composition"
    }
  ]
}
```

### POST /artworks/{id}/favorite
Add artwork to favorites.

**Headers:** `Authorization: Bearer <token>`

**Response:** `201 Created`

### DELETE /artworks/{id}/favorite
Remove artwork from favorites.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

## Collection Endpoints

### GET /collections
List user's collections.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`, `page_size`, `sort`, `order`
- `collection_type` (string)
- `is_public` (boolean)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "uuid": "coll_789ghi",
      "name": "Impressionist Masters",
      "description": "My favorite impressionist paintings",
      "cover_artwork": {
        "id": 1,
        "thumbnail_url": "https://cdn.example.com/thumbnails/1.jpg"
      },
      "collection_type": "custom",
      "artwork_count": 45,
      "is_public": true,
      "created_at": "2026-02-01T00:00:00Z",
      "updated_at": "2026-07-26T02:23:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### GET /collections/{id}
Get collection details with artworks.

**Response:** `200 OK`
```json
{
  "id": 1,
  "uuid": "coll_789ghi",
  "name": "Impressionist Masters",
  "description": "My favorite impressionist paintings",
  "cover_artwork": { /* artwork object */ },
  "collection_type": "custom",
  "sort_order": "manual",
  "artwork_count": 45,
  "is_public": true,
  "artworks": [
    { /* artwork object */ }
  ],
  "created_at": "2026-02-01T00:00:00Z",
  "updated_at": "2026-07-26T02:23:00Z"
}
```

### POST /collections
Create new collection.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Nature Photography",
  "description": "Beautiful nature photos",
  "collection_type": "custom",
  "is_public": false
}
```

**Response:** `201 Created` (returns collection object)

### PATCH /collections/{id}
Update collection.

**Response:** `200 OK` (returns updated collection object)

### DELETE /collections/{id}
Delete collection.

**Response:** `204 No Content`

### POST /collections/{id}/artworks/{artwork_id}
Add artwork to collection.

**Headers:** `Authorization: Bearer <token>`

**Response:** `201 Created`

### DELETE /collections/{id}/artworks/{artwork_id}
Remove artwork from collection.

**Response:** `204 No Content`

### PUT /collections/{id}/artworks/reorder
Reorder artworks in collection.

**Request:**
```json
{
  "artwork_ids": [5, 3, 1, 7, 2]
}
```

**Response:** `200 OK`

## Playlist Endpoints

### GET /playlists
List user's playlists.

**Similar structure to collections endpoints**

### GET /playlists/{id}
Get playlist details.

### POST /playlists
Create new playlist.

**Request:**
```json
{
  "name": "Evening Relaxation",
  "description": "Calming artworks for evening display",
  "shuffle_mode": false,
  "repeat_mode": "all",
  "interval_seconds": 1800,
  "is_public": false
}
```

### PATCH /playlists/{id}
Update playlist.

### DELETE /playlists/{id}
Delete playlist.

### POST /playlists/{id}/items/{artwork_id}
Add artwork to playlist.

### DELETE /playlists/{id}/items/{artwork_id}
Remove artwork from playlist.

### PUT /playlists/{id}/items/reorder
Reorder playlist items.

### POST /playlists/{id}/play
Start playing playlist on a device.

**Request:**
```json
{
  "device_id": 1
}
```

**Response:** `200 OK`

## Artist Endpoints

### GET /artists
List artists.

**Query Parameters:**
- `page`, `page_size`, `sort`, `order`
- `search` (string)
- `nationality` (string)
- `birth_year_min`, `birth_year_max` (integer)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "uuid": "artist_456def",
      "name": "Vincent van Gogh",
      "biography": "Dutch Post-Impressionist painter...",
      "birth_year": 1853,
      "death_year": 1890,
      "nationality": "Dutch",
      "artwork_count": 15
    }
  ],
  "total": 450,
  "page": 1,
  "page_size": 20,
  "total_pages": 23
}
```

### GET /artists/{id}
Get artist details with artworks.

**Response:** `200 OK`
```json
{
  "id": 1,
  "uuid": "artist_456def",
  "name": "Vincent van Gogh",
  "biography": "Dutch Post-Impressionist painter known for...",
  "birth_year": 1853,
  "death_year": 1890,
  "nationality": "Dutch",
  "artwork_count": 15,
  "artworks": [
    { /* artwork object */ }
  ]
}
```

## Device Endpoints

### GET /devices
List user's registered devices.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "uuid": "dev_abc123",
      "name": "Living Room Frame TV",
      "device_type": "samsung_tv",
      "model": "QN55LS03BAFXZA",
      "home": {
        "id": 1,
        "name": "My Home"
      },
      "max_width": 3840,
      "max_height": 2160,
      "is_online": true,
      "last_seen_at": "2026-07-26T02:20:00Z",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "total": 3
}
```

### GET /devices/{id}
Get device details.

### POST /devices
Register new device.

**Request:**
```json
{
  "name": "Bedroom Frame TV",
  "device_type": "samsung_tv",
  "model": "QN43LS03BAFXZA",
  "home_id": 1,
  "max_width": 3840,
  "max_height": 2160
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "uuid": "dev_xyz789",
  "api_key": "sk_live_abc123xyz789...",
  /* other device fields */
}
```

### PATCH /devices/{id}
Update device settings.

### DELETE /devices/{id}
Unregister device.

**Response:** `204 No Content`

### POST /devices/{id}/heartbeat
Device heartbeat to update online status.

**Headers:** `Authorization: Bearer <device_api_key>`

**Request:**
```json
{
  "ip_address": "192.168.1.100",
  "current_artwork_id": 1234
}
```

**Response:** `200 OK`

### GET /devices/{id}/next-artwork
Get next artwork to display based on schedule.

**Headers:** `Authorization: Bearer <device_api_key>`

**Response:** `200 OK`
```json
{
  "artwork": { /* full artwork object */ },
  "display_duration": 1800,
  "transition_effect": "fade"
}
```

## Schedule Endpoints

### GET /schedules
List user's schedules.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "uuid": "sched_def456",
      "name": "Morning Nature",
      "description": "Display nature photos in the morning",
      "device": {
        "id": 1,
        "name": "Living Room Frame TV"
      },
      "is_enabled": true,
      "priority": 10,
      "time_rules": {
        "days_of_week": [1, 2, 3, 4, 5],
        "time_range": {
          "start": "06:00",
          "end": "10:00"
        }
      },
      "content_type": "collection",
      "content_id": 5,
      "interval_seconds": 3600,
      "shuffle_mode": true,
      "created_at": "2026-03-01T00:00:00Z"
    }
  ],
  "total": 5
}
```

### GET /schedules/{id}
Get schedule details.

### POST /schedules
Create new schedule.

**Request:**
```json
{
  "name": "Evening Abstract Art",
  "device_id": 1,
  "is_enabled": true,
  "priority": 5,
  "time_rules": {
    "days_of_week": [0, 1, 2, 3, 4, 5, 6],
    "time_range": {
      "start": "18:00",
      "end": "23:00"
    }
  },
  "content_type": "collection",
  "content_id": 3,
  "interval_seconds": 1800,
  "shuffle_mode": false
}
```

**Response:** `201 Created` (returns schedule object)

### PATCH /schedules/{id}
Update schedule.

### DELETE /schedules/{id}
Delete schedule.

## Search Endpoints

### GET /search
Global search across artworks, artists, and collections.

**Query Parameters:**
- `q` (string, required)
- `type` (string, options: "all", "artworks", "artists", "collections")
- `limit` (integer, default: 20)

**Response:** `200 OK`
```json
{
  "artworks": {
    "items": [ /* artwork objects */ ],
    "total": 45
  },
  "artists": {
    "items": [ /* artist objects */ ],
    "total": 3
  },
  "collections": {
    "items": [ /* collection objects */ ],
    "total": 7
  },
  "query": "impressionism",
  "took_ms": 45
}
```

### GET /search/suggest
Autocomplete suggestions.

**Query Parameters:**
- `q` (string, required)
- `limit` (integer, default: 10)

**Response:** `200 OK`
```json
{
  "suggestions": [
    {
      "text": "impressionism",
      "type": "tag",
      "count": 150
    },
    {
      "text": "Claude Monet",
      "type": "artist",
      "count": 45
    }
  ]
}
```

## Integration Endpoints

### GET /integrations
List available integrations.

**Response:** `200 OK`
```json
{
  "items": [
    {
      "provider": "google_drive",
      "name": "Google Drive",
      "icon_url": "https://...",
      "is_connected": true,
      "last_sync_at": "2026-07-26T01:00:00Z"
    },
    {
      "provider": "unsplash",
      "name": "Unsplash",
      "icon_url": "https://...",
      "is_connected": false
    }
  ]
}
```

### POST /integrations/{provider}/connect
Initiate OAuth flow for integration.

**Response:** `200 OK`
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### POST /integrations/{provider}/callback
OAuth callback handler.

### DELETE /integrations/{provider}
Disconnect integration.

### POST /integrations/{provider}/sync
Trigger manual sync.

**Response:** `202 Accepted`
```json
{
  "job_id": "job_abc123",
  "status": "pending"
}
```

## AI Endpoints

### POST /ai/generate-description
Generate artwork description using AI.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "artwork_id": 1
}
```

**Response:** `200 OK`
```json
{
  "description": "This painting captures a serene evening scene...",
  "provider": "openai",
  "model": "gpt-4",
  "cost_credits": 0.05
}
```

### POST /ai/generate-tags
Generate tags for artwork.

**Request:**
```json
{
  "artwork_id": 1
}
```

**Response:** `200 OK`
```json
{
  "tags": ["sunset", "nature", "landscape", "peaceful", "golden hour"],
  "confidence_scores": [0.95, 0.92, 0.88, 0.85, 0.82]
}
```

### POST /ai/generate-artwork
Generate new artwork with AI.

**Request:**
```json
{
  "prompt": "A serene mountain landscape at sunset",
  "provider": "openai",
  "style": "photorealistic",
  "aspect_ratio": "16:9"
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "job_xyz789",
  "status": "pending",
  "estimated_time_seconds": 30
}
```

### GET /ai/recommendations
Get personalized artwork recommendations.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (integer, default: 20)
- `recommendation_type` (string)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "artwork": { /* artwork object */ },
      "score": 0.95,
      "reason": "Based on your viewing history"
    }
  ]
}
```

## Analytics Endpoints

### GET /analytics/overview
Get user analytics overview.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `period` (string, options: "day", "week", "month", "year")

**Response:** `200 OK`
```json
{
  "period": "month",
  "total_views": 1234,
  "unique_artworks_viewed": 567,
  "total_time_spent_seconds": 45000,
  "favorite_artists": [
    {
      "artist": { /* artist object */ },
      "view_count": 89
    }
  ],
  "popular_tags": [
    {"tag": "impressionism", "count": 156},
    {"tag": "landscape", "count": 134}
  ],
  "viewing_by_hour": {
    "0": 5, "1": 2, "2": 0, ..., "23": 12
  }
}
```

### GET /analytics/devices/{id}/stats
Get device-specific analytics.

**Response:** `200 OK`
```json
{
  "device": { /* device object */ },
  "total_views": 5678,
  "total_runtime_hours": 720,
  "most_displayed_artworks": [
    {
      "artwork": { /* artwork object */ },
      "display_count": 45,
      "total_duration_seconds": 81000
    }
  ]
}
```

## Admin Endpoints

### GET /admin/users
List all users (admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Query Parameters:**
- Standard pagination and filtering

**Response:** `200 OK`

### GET /admin/stats
System-wide statistics.

**Response:** `200 OK`
```json
{
  "total_users": 10234,
  "active_users_30d": 5678,
  "total_artworks": 1234567,
  "total_views_30d": 8765432,
  "storage_used_gb": 5678.9,
  "top_sources": [
    {"source": "user_upload", "count": 500000},
    {"source": "met_museum", "count": 300000}
  ]
}
```

## WebSocket Endpoints

### WS /ws/device/{device_id}
Real-time device communication.

**Messages:**
```json
// Server → Device: Display new artwork
{
  "type": "display_artwork",
  "artwork": { /* artwork object */ },
  "duration": 1800
}

// Device → Server: Status update
{
  "type": "status",
  "is_online": true,
  "current_artwork_id": 1234
}

// Server → Device: Command
{
  "type": "command",
  "action": "pause" | "resume" | "next" | "previous"
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST that creates resource |
| 202 | Accepted | Request accepted for async processing |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (e.g., duplicate email) |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server overloaded or maintenance |

## Response Headers

### Standard Headers
```
Content-Type: application/json
X-Request-ID: req_abc123xyz
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1627390800
X-API-Version: 1.0
```

### Pagination Headers
```
X-Total-Count: 1234
X-Page: 1
X-Page-Size: 20
X-Total-Pages: 62
Link: <https://api.example.com/artworks?page=2>; rel="next"
```

## Pagination

Standard pagination for list endpoints:

**Query Parameters:**
- `page` (integer, 1-indexed)
- `page_size` (integer, max 100)

**Response:**
```json
{
  "items": [ /* array of resources */ ],
  "total": 1234,
  "page": 1,
  "page_size": 20,
  "total_pages": 62
}
```

## Filtering

Common filter patterns:

- **Equality:** `?status=active`
- **Multiple values:** `?tags=impressionism,landscape`
- **Range:** `?year_min=1800&year_max=1900`
- **Boolean:** `?is_public=true`
- **Search:** `?search=van+gogh`

## Sorting

Sort with `sort` and `order` parameters:

- `?sort=created_at&order=desc`
- `?sort=title&order=asc`

Multiple sorts: `?sort=year,-title` (comma-separated, `-` for descending)

## Field Selection

Request specific fields only:

- `?fields=id,title,thumbnail_url`

Useful for reducing response size in mobile apps.

## Caching

API responses include caching headers:

```
Cache-Control: public, max-age=300
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Fri, 26 Jul 2026 02:23:00 GMT
```

Clients should use `If-None-Match` and `If-Modified-Since` headers.

## API Documentation

Interactive API documentation available at:

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

---

**API Version:** 1.0  
**Last Updated:** 2026-07-26  
**OpenAPI Specification:** 3.0.3
