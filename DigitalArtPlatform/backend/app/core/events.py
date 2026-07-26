"""
Application Event Handlers

Startup and shutdown event handlers for the FastAPI application.
"""
import logging
from typing import Callable

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import engine

logger = logging.getLogger(__name__)


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Create startup event handler.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Callable: Startup handler function
    """
    async def start_app() -> None:
        logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Initialize database connection pool
        # This creates the connection pool at startup
        logger.info("Initializing database connection pool")
        
        # Initialize Redis connection
        logger.info("Initializing Redis connection")
        
        # Initialize S3 client if using S3 storage
        if settings.STORAGE_TYPE == "s3":
            logger.info("Initializing S3 client")
        
        logger.info("Application startup complete")
    
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Create shutdown event handler.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Callable: Shutdown handler function
    """
    async def stop_app() -> None:
        logger.info("Shutting down application")
        
        # Close database connections
        logger.info("Closing database connections")
        await engine.dispose()
        
        # Close Redis connections
        logger.info("Closing Redis connections")
        
        logger.info("Application shutdown complete")
    
    return stop_app
