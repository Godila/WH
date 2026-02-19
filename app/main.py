from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import async_session
from app.seed import seed_database
from app.api import auth, sources, distribution_centers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events:
    - Startup: Run database migrations and seed initial data
    - Shutdown: Cleanup resources if needed
    """
    # Startup: seed database with initial data
    async with async_session() as db:
        await seed_database(db)
    
    yield
    
    # Shutdown: cleanup if needed (currently nothing to clean up)


# Create FastAPI application
app = FastAPI(
    title="WMS Marketplace",
    description="""
Warehouse Management System for Marketplace Fulfillment.

A system for managing inventory across two warehouses (Stock and DefectStock) 
with support for 9 operation types and complete movement journal.

## Authentication

All endpoints require JWT authentication. Use `/api/auth/login` to get a token.

## Features

- JWT-based authentication
- Source management (suppliers, pickup points)
- Distribution center management (WB, Ozon)
- Stock operations (Phase 3)
- Movement journal (Phase 3)
- Excel import (Phase 4)
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register API routers
app.include_router(auth.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(distribution_centers.router, prefix="/api")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status indicating the service is running
    """
    return {"status": "ok"}
