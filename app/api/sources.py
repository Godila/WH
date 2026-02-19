from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.source import Source
from app.models.user import User
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=list[SourceResponse])
async def list_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Source]:
    """
    List all sources.
    
    Returns all sources in the system.
    Requires authentication.
    """
    result = await db.execute(select(Source).order_by(Source.name))
    return list(result.scalars().all())


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    data: SourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Source:
    """
    Create a new source.
    
    Args:
        data: Source creation data
        
    Returns:
        Created source
        
    Raises:
        HTTPException: 400 if source with name already exists
    """
    # Check if source with same name exists
    existing = await db.execute(
        select(Source).where(Source.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source with name '{data.name}' already exists"
        )
    
    source = Source(**data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Source:
    """
    Get a source by ID.
    
    Args:
        source_id: UUID of the source
        
    Returns:
        Source data
        
    Raises:
        HTTPException: 404 if source not found
    """
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    return source


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: UUID,
    data: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Source:
    """
    Update a source.
    
    Args:
        source_id: UUID of the source
        data: Update data (partial updates supported)
        
    Returns:
        Updated source
        
    Raises:
        HTTPException: 404 if source not found
    """
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Update only provided fields
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(source, key, value)
    
    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a source.
    
    Args:
        source_id: UUID of the source
        
    Raises:
        HTTPException: 404 if source not found
    """
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    await db.delete(source)
    await db.commit()
