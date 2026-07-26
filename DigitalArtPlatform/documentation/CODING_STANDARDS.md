# Coding Standards

## Overview

This document defines the coding standards, style guides, and best practices for the Digital Art Platform project. All contributors must follow these guidelines to maintain code quality and consistency.

## General Principles

### 1. Code Quality
- **Clean Code**: Write self-documenting, readable code
- **DRY (Don't Repeat Yourself)**: Extract common logic into reusable functions
- **SOLID Principles**: Follow object-oriented design principles
- **YAGNI (You Aren't Gonna Need It)**: Don't add functionality until needed
- **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones

### 2. Code Reviews
- All code must be reviewed before merging
- Use pull request templates
- Address all review comments
- Keep PRs small and focused (< 500 lines preferred)
- Include tests with code changes

### 3. Testing
- Minimum 80% code coverage
- Write tests before or alongside code (TDD encouraged)
- Test edge cases and error scenarios
- Use descriptive test names
- Mock external dependencies

### 4. Documentation
- Document all public APIs
- Include docstrings for functions and classes
- Update README files when adding features
- Document architectural decisions (ADRs)
- Keep inline comments minimal and meaningful

## Python (Backend)

### Style Guide
Follow **PEP 8** with these specific guidelines:

#### Formatting
```python
# Line length: 100 characters (not 79)
MAX_LINE_LENGTH = 100

# Use 4 spaces for indentation (no tabs)
def function_name():
    if condition:
        do_something()

# Two blank lines between top-level definitions
class MyClass:
    pass


def my_function():
    pass
```

#### Naming Conventions
```python
# Classes: PascalCase
class ArtworkService:
    pass

# Functions and variables: snake_case
def get_artwork_by_id(artwork_id: int):
    user_name = "John"
    
# Constants: UPPER_SNAKE_CASE
MAX_UPLOAD_SIZE = 10485760
API_VERSION = "v1"

# Private members: leading underscore
class MyClass:
    def __init__(self):
        self._private_var = 42
    
    def _private_method(self):
        pass

# Module names: lowercase with underscores
# artwork_service.py
# user_repository.py
```

#### Type Hints
Always use type hints for function parameters and return values:

```python
from typing import List, Optional, Dict, Any
from datetime import datetime

def get_artworks(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Get artworks for a user.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of artworks to return
        offset: Number of artworks to skip
        tags: Optional list of tags to filter by
        
    Returns:
        List of artwork dictionaries
        
    Raises:
        ValueError: If user_id is invalid
        DatabaseError: If database query fails
    """
    if user_id < 1:
        raise ValueError("Invalid user_id")
    
    # Implementation
    return []
```

#### Docstrings
Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Brief description of what this function does.
    
    More detailed explanation if needed. This can span
    multiple lines and include examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> complex_function("test", 42)
        True
    """
    pass
```

#### Imports
```python
# Standard library imports first
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

# Third-party imports second
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np

# Local application imports last
from app.models.user import User
from app.services.artwork_service import ArtworkService
from app.core.config import settings

# Use absolute imports, not relative
# Good: from app.models.user import User
# Bad:  from ..models.user import User
```

#### Exception Handling
```python
# Be specific with exceptions
try:
    artwork = get_artwork(artwork_id)
except ArtworkNotFoundError as e:
    logger.error(f"Artwork {artwork_id} not found: {e}")
    raise HTTPException(status_code=404, detail="Artwork not found")
except DatabaseError as e:
    logger.exception("Database error occurred")
    raise HTTPException(status_code=500, detail="Internal server error")

# Don't use bare except
# Bad:
try:
    do_something()
except:  # Don't do this!
    pass

# Use context managers for resources
with open("file.txt") as f:
    content = f.read()
```

#### Async/Await
```python
# Use async/await for I/O operations
async def get_artwork(artwork_id: int) -> Artwork:
    async with get_db_session() as session:
        result = await session.execute(
            select(Artwork).where(Artwork.id == artwork_id)
        )
        return result.scalar_one()

# Don't mix sync and async unnecessarily
# Use asyncio.to_thread() for CPU-bound work
```

### Project Structure
```python
# Services should be classes with dependency injection
class ArtworkService:
    def __init__(
        self,
        artwork_repository: ArtworkRepository,
        image_service: ImageService,
        cache: CacheService
    ):
        self.artwork_repo = artwork_repository
        self.image_service = image_service
        self.cache = cache
    
    async def get_artwork(self, artwork_id: int) -> Artwork:
        # Check cache first
        cached = await self.cache.get(f"artwork:{artwork_id}")
        if cached:
            return cached
        
        # Fetch from database
        artwork = await self.artwork_repo.get_by_id(artwork_id)
        
        # Cache result
        await self.cache.set(f"artwork:{artwork_id}", artwork, ttl=3600)
        
        return artwork
```

### Testing
Use **pytest** for testing:

```python
# test_artwork_service.py
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def artwork_service():
    """Create ArtworkService with mocked dependencies."""
    mock_repo = Mock(spec=ArtworkRepository)
    mock_image_service = Mock(spec=ImageService)
    mock_cache = Mock(spec=CacheService)
    
    return ArtworkService(
        artwork_repository=mock_repo,
        image_service=mock_image_service,
        cache=mock_cache
    )

@pytest.mark.asyncio
async def test_get_artwork_from_cache(artwork_service):
    """Test that cached artworks are returned without database query."""
    # Arrange
    artwork_id = 1
    cached_artwork = Artwork(id=artwork_id, title="Test")
    artwork_service.cache.get = AsyncMock(return_value=cached_artwork)
    
    # Act
    result = await artwork_service.get_artwork(artwork_id)
    
    # Assert
    assert result == cached_artwork
    artwork_service.cache.get.assert_called_once_with(f"artwork:{artwork_id}")
    artwork_service.artwork_repo.get_by_id.assert_not_called()

@pytest.mark.asyncio
async def test_get_artwork_not_found(artwork_service):
    """Test that ArtworkNotFoundError is raised when artwork doesn't exist."""
    # Arrange
    artwork_id = 999
    artwork_service.cache.get = AsyncMock(return_value=None)
    artwork_service.artwork_repo.get_by_id = AsyncMock(
        side_effect=ArtworkNotFoundError()
    )
    
    # Act & Assert
    with pytest.raises(ArtworkNotFoundError):
        await artwork_service.get_artwork(artwork_id)
```

### Linting & Formatting

Required tools:
- **black**: Code formatter
- **isort**: Import sorter
- **flake8**: Linter
- **mypy**: Type checker
- **pylint**: Additional linting

Configuration in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pylint.messages_control]
max-line-length = 100
disable = ["C0111"]  # missing-docstring for tests
```

Run before committing:
```bash
# Format code
black app/
isort app/

# Check types
mypy app/

# Lint
flake8 app/
pylint app/
```

## TypeScript (Web Dashboard)

### Style Guide
Follow **Airbnb TypeScript Style Guide** with modifications:

#### Naming Conventions
```typescript
// Interfaces and Types: PascalCase
interface ArtworkData {
  id: number;
  title: string;
}

type ArtworkStatus = 'active' | 'archived';

// Classes: PascalCase
class ArtworkService {
  private readonly apiClient: ApiClient;
  
  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }
}

// Functions and variables: camelCase
const getArtworkById = (id: number): Promise<Artwork> => {
  return apiClient.get(`/artworks/${id}`);
};

// Constants: UPPER_SNAKE_CASE
const MAX_UPLOAD_SIZE = 10485760;
const API_BASE_URL = 'https://api.example.com';

// Files: kebab-case
// artwork-service.ts
// user-profile.component.tsx
```

#### TypeScript Best Practices
```typescript
// Always use strict type checking
// tsconfig.json: "strict": true

// Use interfaces for objects
interface Artwork {
  id: number;
  title: string;
  artist?: Artist;  // Optional properties with ?
  tags: string[];   // Use specific types, not 'any'
}

// Use union types for variants
type RequestStatus = 'idle' | 'loading' | 'success' | 'error';

// Use generics for reusable types
interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// Avoid 'any' - use 'unknown' if type is truly unknown
const parseJson = (json: string): unknown => {
  return JSON.parse(json);
};

// Use type guards
function isArtwork(obj: unknown): obj is Artwork {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'title' in obj
  );
}
```

#### React Best Practices
```tsx
// Use functional components with hooks
import { useState, useEffect, useCallback } from 'react';

interface ArtworkCardProps {
  artwork: Artwork;
  onFavorite?: (id: number) => void;
}

export const ArtworkCard: React.FC<ArtworkCardProps> = ({ 
  artwork, 
  onFavorite 
}) => {
  const [isFavorited, setIsFavorited] = useState(false);
  
  const handleFavorite = useCallback(() => {
    setIsFavorited(!isFavorited);
    onFavorite?.(artwork.id);
  }, [isFavorited, artwork.id, onFavorite]);
  
  return (
    <div className="artwork-card">
      <img src={artwork.thumbnailUrl} alt={artwork.title} />
      <h3>{artwork.title}</h3>
      <button onClick={handleFavorite}>
        {isFavorited ? 'Unfavorite' : 'Favorite'}
      </button>
    </div>
  );
};

// Use proper prop types
// Avoid inline object creation in props
// Use useCallback for event handlers
// Use useMemo for expensive computations
```

#### Imports
```typescript
// React imports first
import React, { useState, useEffect } from 'react';

// Third-party library imports
import { useQuery } from '@tanstack/react-query';
import { clsx } from 'clsx';

// Local imports (absolute paths using path aliases)
import { ArtworkService } from '@/services/artwork-service';
import { Button } from '@/components/ui/button';
import { Artwork } from '@/types/artwork';

// Style imports last
import styles from './artwork-card.module.css';
```

### Linting & Formatting

Tools:
- **ESLint**: Linter
- **Prettier**: Code formatter
- **typescript-eslint**: TypeScript-specific rules

Configuration in `.eslintrc.js`:

```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier'
  ],
  rules: {
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    'react/react-in-jsx-scope': 'off',  // Not needed in React 18+
    'react/prop-types': 'off',  // Using TypeScript
  }
};
```

## Swift (iOS App)

### Style Guide
Follow **Swift API Design Guidelines** and **Ray Wenderlich Swift Style Guide**

#### Naming Conventions
```swift
// Classes, Structs, Enums, Protocols: PascalCase
class ArtworkService { }
struct Artwork { }
enum ArtworkStatus { }
protocol ArtworkRepositoryProtocol { }

// Functions, variables, parameters: camelCase
func fetchArtwork(by id: Int) -> Artwork? { }
var artworkTitle: String = ""
let maximumUploadSize = 10_485_760

// Constants: camelCase (not UPPER_CASE)
let apiBaseURL = "https://api.example.com"

// Enums: PascalCase for type, camelCase for values
enum LoadingState {
    case idle
    case loading
    case loaded(Artwork)
    case failed(Error)
}
```

#### SwiftUI Best Practices
```swift
import SwiftUI

struct ArtworkCardView: View {
    let artwork: Artwork
    @State private var isFavorited = false
    @EnvironmentObject private var artworkService: ArtworkService
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            AsyncImage(url: URL(string: artwork.thumbnailURL)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                ProgressView()
            }
            .frame(height: 200)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            
            Text(artwork.title)
                .font(.headline)
            
            Button(action: toggleFavorite) {
                Label(
                    isFavorited ? "Unfavorite" : "Favorite",
                    systemImage: isFavorited ? "heart.fill" : "heart"
                )
            }
        }
        .padding()
    }
    
    private func toggleFavorite() {
        isFavorited.toggle()
        Task {
            await artworkService.toggleFavorite(artwork.id)
        }
    }
}
```

#### MVVM Architecture
```swift
// Model
struct Artwork: Identifiable, Codable {
    let id: Int
    let title: String
    let thumbnailURL: String
    let artist: Artist?
}

// ViewModel
@MainActor
class ArtworkListViewModel: ObservableObject {
    @Published var artworks: [Artwork] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let artworkService: ArtworkService
    
    init(artworkService: ArtworkService = .shared) {
        self.artworkService = artworkService
    }
    
    func loadArtworks() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            artworks = try await artworkService.fetchArtworks()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// View
struct ArtworkListView: View {
    @StateObject private var viewModel = ArtworkListViewModel()
    
    var body: some View {
        List(viewModel.artworks) { artwork in
            ArtworkCardView(artwork: artwork)
        }
        .task {
            await viewModel.loadArtworks()
        }
    }
}
```

## JavaScript (Samsung TV App)

### Style Guide
Follow **Airbnb JavaScript Style Guide**

#### ES6+ Features
```javascript
// Use const/let, not var
const MAX_RETRIES = 3;
let currentArtwork = null;

// Arrow functions
const fetchArtwork = async (id) => {
  const response = await fetch(`/api/artworks/${id}`);
  return response.json();
};

// Destructuring
const { title, artist, thumbnailUrl } = artwork;
const [first, ...rest] = artworks;

// Template literals
const message = `Displaying artwork: ${artwork.title} by ${artwork.artist}`;

// Async/await over promises
const loadArtwork = async () => {
  try {
    const artwork = await fetchArtwork(id);
    displayArtwork(artwork);
  } catch (error) {
    console.error('Failed to load artwork:', error);
  }
};
```

## Git Workflow

### Branch Naming
```
main              # Production-ready code
develop           # Development branch
feature/add-ai-recommendations
bugfix/fix-image-upload
hotfix/security-patch
release/v1.0.0
```

### Commit Messages
Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semi-colons, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add artwork recommendation endpoint

Implement AI-powered artwork recommendations based on user viewing history
and preferences. Uses OpenAI embeddings for similarity search.

Closes #123

---

fix(web): prevent memory leak in image carousel

The carousel was not properly cleaning up event listeners
when unmounting, causing memory leaks after navigation.

---

docs: update API documentation for authentication

Add examples for OAuth flow and refresh token usage.
```

### Pull Requests
- Use the PR template
- Link related issues
- Keep PRs focused and small
- Request review from relevant team members
- Update documentation as needed
- Ensure CI passes before requesting review

## Code Review Guidelines

### As a Reviewer
- Be respectful and constructive
- Explain the "why" behind suggestions
- Approve if no blocking issues
- Use "Request Changes" sparingly
- Praise good code

### As an Author
- Respond to all comments
- Don't take feedback personally
- Ask for clarification if needed
- Make requested changes or explain why not
- Thank reviewers

## Security

### Never Commit
- API keys or secrets
- Passwords or tokens
- Private keys
- `.env` files with real credentials

### Use Environment Variables
```python
# Good
DATABASE_URL = os.getenv("DATABASE_URL")

# Bad
DATABASE_URL = "postgresql://user:password@localhost/db"
```

### Input Validation
```python
# Always validate and sanitize user input
def create_artwork(data: dict):
    # Validate
    if not data.get("title"):
        raise ValueError("Title is required")
    
    # Sanitize
    title = data["title"].strip()[:500]  # Limit length
    
    # Escape for database (using ORM handles this)
    artwork = Artwork(title=title)
    db.add(artwork)
```

## Performance

### Database Queries
```python
# Use select_related/joinedload to avoid N+1 queries
artworks = await session.execute(
    select(Artwork)
    .options(joinedload(Artwork.artist))
    .limit(20)
)

# Use pagination
artworks = await session.execute(
    select(Artwork)
    .offset(offset)
    .limit(limit)
)

# Use indexes
# Define in model or migration
Index('idx_artwork_title', Artwork.title)
```

### Caching
```python
# Cache expensive operations
@cache(ttl=3600)
async def get_trending_artworks():
    # Expensive query
    return artworks
```

### Async Operations
```python
# Use async for I/O operations
async def fetch_multiple_artworks(ids: List[int]) -> List[Artwork]:
    tasks = [fetch_artwork(id) for id in ids]
    return await asyncio.gather(*tasks)
```

## Accessibility

### Web
```tsx
// Use semantic HTML
<button onClick={handleClick}>Click me</button>
// Not: <div onClick={handleClick}>Click me</div>

// Add ARIA labels
<img src={artwork.url} alt={artwork.title} />
<button aria-label="Favorite this artwork">❤️</button>

// Support keyboard navigation
<div role="button" tabIndex={0} onKeyPress={handleKeyPress}>
```

### iOS
```swift
// Add accessibility labels
Image(artwork.thumbnailURL)
    .accessibilityLabel(artwork.title)

Button("Favorite") { }
    .accessibilityLabel("Favorite \(artwork.title)")
    .accessibilityHint("Double tap to add to favorites")
```

## Logging

### Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

### Format
```python
import logging

logger = logging.getLogger(__name__)

# Good logging
logger.info("User %s created artwork %s", user.id, artwork.id)
logger.error(
    "Failed to process image %s: %s",
    image_id,
    str(error),
    exc_info=True  # Include traceback
)

# Include context
logger.info(
    "Artwork uploaded",
    extra={
        "user_id": user.id,
        "artwork_id": artwork.id,
        "file_size": file_size,
        "duration_ms": elapsed_time
    }
)
```

## Continuous Integration

### Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
```

### CI Pipeline
1. Linting (black, isort, flake8, mypy)
2. Unit tests
3. Integration tests
4. Build Docker image
5. Security scanning
6. Deploy to staging (on main branch)

---

**Version**: 1.0  
**Last Updated**: 2026-07-26  
**Maintainer**: Development Team
