# Shared

Shared models, types, utilities, and resources used across multiple platform components.

## Overview

This directory contains code and resources that are shared between different parts of the Digital Art Platform (backend, web dashboard, mobile apps, etc.). The goal is to maintain consistency and reduce duplication across the platform.

## Contents

```
shared/
├── models/              # Data models and schemas
│   ├── artwork.schema.json
│   ├── user.schema.json
│   ├── collection.schema.json
│   └── device.schema.json
│
├── types/               # TypeScript type definitions
│   ├── artwork.ts
│   ├── user.ts
│   ├── api.ts
│   └── index.ts
│
├── constants/           # Shared constants
│   ├── artwork-sources.json
│   ├── categories.json
│   ├── styles.json
│   └── museums.json
│
├── utils/               # Utility functions
│   ├── image-utils.ts
│   ├── date-utils.ts
│   ├── validation.ts
│   └── formatting.ts
│
├── assets/              # Shared assets
│   ├── icons/
│   ├── fonts/
│   └── images/
│
└── docs/                # Additional documentation
    ├── API_CHANGELOG.md
    └── DATA_MODELS.md
```

## Data Models

### JSON Schemas

JSON Schema definitions for data validation across platforms.

#### Artwork Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "title", "original_url"],
  "properties": {
    "id": {
      "type": "integer",
      "description": "Unique artwork identifier"
    },
    "uuid": {
      "type": "string",
      "format": "uuid",
      "description": "UUID for external references"
    },
    "title": {
      "type": "string",
      "maxLength": 500,
      "description": "Artwork title"
    },
    "description": {
      "type": "string",
      "description": "Artwork description"
    },
    "artist": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "name": { "type": "string" },
        "nationality": { "type": "string" }
      }
    },
    "year": {
      "type": "integer",
      "minimum": -5000,
      "maximum": 2100
    },
    "source": {
      "type": "string",
      "enum": [
        "met_museum",
        "rijksmuseum",
        "art_institute_chicago",
        "user_upload",
        "unsplash",
        "ai_generated"
      ]
    },
    "original_url": {
      "type": "string",
      "format": "uri"
    },
    "thumbnail_url": {
      "type": "string",
      "format": "uri"
    },
    "preview_url": {
      "type": "string",
      "format": "uri"
    },
    "width": {
      "type": "integer",
      "minimum": 1
    },
    "height": {
      "type": "integer",
      "minimum": 1
    },
    "orientation": {
      "type": "string",
      "enum": ["landscape", "portrait", "square"]
    },
    "dominant_colors": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^#[0-9A-Fa-f]{6}$"
      }
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

## TypeScript Types

Shared TypeScript type definitions for type safety across web and mobile apps.

```typescript
// types/artwork.ts
export interface Artwork {
  id: number;
  uuid: string;
  title: string;
  description?: string;
  artist?: Artist;
  year?: number;
  source: ArtworkSource;
  source_id?: string;
  source_url?: string;
  license?: string;
  original_url: string;
  thumbnail_url?: string;
  preview_url?: string;
  high_res_url?: string;
  width: number;
  height: number;
  aspect_ratio: number;
  orientation: 'landscape' | 'portrait' | 'square';
  format: string;
  file_size?: number;
  dominant_colors?: string[];
  average_color?: string;
  medium?: string;
  style?: string;
  tags: string[];
  is_public: boolean;
  is_favorite?: boolean;
  view_count: number;
  favorite_count: number;
  created_at: string;
  updated_at: string;
}

export interface Artist {
  id: number;
  uuid: string;
  name: string;
  biography?: string;
  birth_year?: number;
  death_year?: number;
  nationality?: string;
  artwork_count: number;
}

export type ArtworkSource =
  | 'met_museum'
  | 'rijksmuseum'
  | 'art_institute_chicago'
  | 'national_gallery'
  | 'europeana'
  | 'nasa'
  | 'unsplash'
  | 'pexels'
  | 'user_upload'
  | 'google_drive'
  | 'dropbox'
  | 'onedrive'
  | 'ai_generated';

export interface ArtworkFilters {
  search?: string;
  artist_id?: number;
  source?: ArtworkSource;
  orientation?: 'landscape' | 'portrait' | 'square';
  year_min?: number;
  year_max?: number;
  tags?: string[];
  color?: string;
  is_public?: boolean;
}

export interface ArtworkListResponse {
  items: Artwork[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

```typescript
// types/api.ts
export interface APIResponse<T> {
  data: T;
  message?: string;
}

export interface APIError {
  detail: string;
  error_code: string;
  status_code: number;
  timestamp: string;
  request_id: string;
  errors?: FieldError[];
}

export interface FieldError {
  field: string;
  message: string;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}
```

## Constants

### Artwork Categories

```json
{
  "categories": [
    { "id": "painting", "name": "Painting", "icon": "🎨" },
    { "id": "photography", "name": "Photography", "icon": "📷" },
    { "id": "sculpture", "name": "Sculpture", "icon": "🗿" },
    { "id": "drawing", "name": "Drawing", "icon": "✏️" },
    { "id": "print", "name": "Print", "icon": "🖼️" },
    { "id": "digital", "name": "Digital Art", "icon": "💻" }
  ]
}
```

### Art Styles

```json
{
  "styles": [
    { "id": "impressionism", "name": "Impressionism", "period": "1860-1890" },
    { "id": "expressionism", "name": "Expressionism", "period": "1905-1920" },
    { "id": "cubism", "name": "Cubism", "period": "1907-1914" },
    { "id": "surrealism", "name": "Surrealism", "period": "1920-1930" },
    { "id": "abstract", "name": "Abstract", "period": "1910-present" },
    { "id": "realism", "name": "Realism", "period": "1840-1880" },
    { "id": "baroque", "name": "Baroque", "period": "1600-1750" },
    { "id": "renaissance", "name": "Renaissance", "period": "1400-1600" },
    { "id": "modern", "name": "Modern", "period": "1860-1970" },
    { "id": "contemporary", "name": "Contemporary", "period": "1970-present" }
  ]
}
```

### Museum APIs

```json
{
  "museums": [
    {
      "id": "met",
      "name": "The Metropolitan Museum of Art",
      "api_url": "https://collectionapi.metmuseum.org/public/collection/v1",
      "website": "https://www.metmuseum.org",
      "country": "USA",
      "city": "New York",
      "requires_api_key": false
    },
    {
      "id": "rijksmuseum",
      "name": "Rijksmuseum",
      "api_url": "https://www.rijksmuseum.nl/api",
      "website": "https://www.rijksmuseum.nl",
      "country": "Netherlands",
      "city": "Amsterdam",
      "requires_api_key": true
    },
    {
      "id": "art_institute_chicago",
      "name": "Art Institute of Chicago",
      "api_url": "https://api.artic.edu/api/v1",
      "website": "https://www.artic.edu",
      "country": "USA",
      "city": "Chicago",
      "requires_api_key": false
    }
  ]
}
```

## Utility Functions

### Image Utilities

```typescript
// utils/image-utils.ts

export function calculateAspectRatio(width: number, height: number): number {
  return width / height;
}

export function getOrientation(
  width: number,
  height: number
): 'landscape' | 'portrait' | 'square' {
  const ratio = calculateAspectRatio(width, height);
  
  if (Math.abs(ratio - 1) < 0.1) return 'square';
  return ratio > 1 ? 'landscape' : 'portrait';
}

export function getImageDimensions(url: string): Promise<{
  width: number;
  height: number;
}> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.width, height: img.height });
    img.onerror = reject;
    img.src = url;
  });
}

export function resizeImage(
  originalWidth: number,
  originalHeight: number,
  maxWidth: number,
  maxHeight: number,
  mode: 'fit' | 'fill' | 'cover' = 'fit'
): { width: number; height: number } {
  const aspectRatio = originalWidth / originalHeight;
  const targetAspectRatio = maxWidth / maxHeight;
  
  let width: number;
  let height: number;
  
  switch (mode) {
    case 'fit':
      if (aspectRatio > targetAspectRatio) {
        width = maxWidth;
        height = maxWidth / aspectRatio;
      } else {
        height = maxHeight;
        width = maxHeight * aspectRatio;
      }
      break;
    
    case 'fill':
      width = maxWidth;
      height = maxHeight;
      break;
    
    case 'cover':
      if (aspectRatio > targetAspectRatio) {
        height = maxHeight;
        width = maxHeight * aspectRatio;
      } else {
        width = maxWidth;
        height = maxWidth / aspectRatio;
      }
      break;
  }
  
  return { width: Math.round(width), height: Math.round(height) };
}

export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

export function rgbToHex(r: number, g: number, b: number): string {
  return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
}
```

### Date Utilities

```typescript
// utils/date-utils.ts

export function formatDate(date: string | Date, format: string = 'long'): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  
  const options: Intl.DateTimeFormatOptions =
    format === 'long'
      ? { year: 'numeric', month: 'long', day: 'numeric' }
      : format === 'short'
      ? { year: 'numeric', month: 'short', day: 'numeric' }
      : { year: 'numeric', month: '2-digit', day: '2-digit' };
  
  return d.toLocaleDateString(undefined, options);
}

export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 7) return formatDate(d, 'short');
  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  return 'Just now';
}

export function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}
```

### Validation

```typescript
// utils/validation.ts

export function validateEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

export function validateURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

export function validateHexColor(color: string): boolean {
  const re = /^#[0-9A-Fa-f]{6}$/;
  return re.test(color);
}

export function validateYear(year: number): boolean {
  return year >= -5000 && year <= 2100;
}
```

## Usage

### In TypeScript Projects

```typescript
import { Artwork, ArtworkFilters } from '@shared/types';
import { formatDate, formatRelativeTime } from '@shared/utils/date-utils';
import { resizeImage, getOrientation } from '@shared/utils/image-utils';

const artwork: Artwork = {
  // ...
};

const formattedDate = formatDate(artwork.created_at);
const orientation = getOrientation(artwork.width, artwork.height);
```

### In Python Projects

```python
import json
from pathlib import Path

# Load constants
def load_museums():
    path = Path(__file__).parent / 'shared' / 'constants' / 'museums.json'
    with open(path) as f:
        return json.load(f)['museums']

museums = load_museums()
```

## Contributing

When adding shared code:

1. Ensure it's truly shared across multiple components
2. Document the code thoroughly
3. Add type definitions for TypeScript
4. Add JSON schemas for data models
5. Write tests if applicable
6. Update this README

## License

MIT License - see [LICENSE](../LICENSE) file for details.
