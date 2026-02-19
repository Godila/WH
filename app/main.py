from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import async_session
from app.seed import seed_database


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
    description="Warehouse Management System for Marketplace Fulfillment",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status indicating the service is running
    """
    return {"status": "ok"}
