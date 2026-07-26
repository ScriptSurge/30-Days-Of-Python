"""
API v1 Router

Aggregates all API v1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# TODO: Add more routers as they are implemented
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(artworks.router, prefix="/artworks", tags=["artworks"])
# api_router.include_router(collections.router, prefix="/collections", tags=["collections"])
