from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.distribution_center import DistributionCenter
from app.models.user import User
from app.schemas.distribution_center import DCCreate, DCUpdate, DCResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/distribution-centers", tags=["distribution-centers"])


@router.get("/", response_model=list[DCResponse])
async def list_distribution_centers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DistributionCenter]:
    """
    List all distribution centers.
    
    Returns all distribution centers in the system.
    Requires authentication.
    """
    result = await db.execute(
        select(DistributionCenter).order_by(DistributionCenter.marketplace, DistributionCenter.code)
    )
    return list(result.scalars().all())


@router.post("/", response_model=DCResponse, status_code=status.HTTP_201_CREATED)
async def create_distribution_center(
    data: DCCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DistributionCenter:
    """
    Create a new distribution center.
    
    Args:
        data: Distribution center creation data
        
    Returns:
        Created distribution center
        
    Raises:
        HTTPException: 400 if DC with code already exists
    """
    # Check if DC with same code exists
    existing = await db.execute(
        select(DistributionCenter).where(DistributionCenter.code == data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Distribution center with code '{data.code}' already exists"
        )
    
    dc = DistributionCenter(**data.model_dump())
    db.add(dc)
    await db.commit()
    await db.refresh(dc)
    return dc


@router.get("/{dc_id}", response_model=DCResponse)
async def get_distribution_center(
    dc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DistributionCenter:
    """
    Get a distribution center by ID.
    
    Args:
        dc_id: UUID of the distribution center
        
    Returns:
        Distribution center data
        
    Raises:
        HTTPException: 404 if distribution center not found
    """
    result = await db.execute(
        select(DistributionCenter).where(DistributionCenter.id == dc_id)
    )
    dc = result.scalar_one_or_none()
    
    if not dc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Distribution center not found"
        )
    
    return dc


@router.put("/{dc_id}", response_model=DCResponse)
async def update_distribution_center(
    dc_id: UUID,
    data: DCUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DistributionCenter:
    """
    Update a distribution center.
    
    Args:
        dc_id: UUID of the distribution center
        data: Update data (partial updates supported)
        
    Returns:
        Updated distribution center
        
    Raises:
        HTTPException: 404 if distribution center not found
    """
    result = await db.execute(
        select(DistributionCenter).where(DistributionCenter.id == dc_id)
    )
    dc = result.scalar_one_or_none()
    
    if not dc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Distribution center not found"
        )
    
    # Update only provided fields
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dc, key, value)
    
    await db.commit()
    await db.refresh(dc)
    return dc


@router.delete("/{dc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_distribution_center(
    dc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a distribution center.
    
    Args:
        dc_id: UUID of the distribution center
        
    Raises:
        HTTPException: 404 if distribution center not found
    """
    result = await db.execute(
        select(DistributionCenter).where(DistributionCenter.id == dc_id)
    )
    dc = result.scalar_one_or_none()
    
    if not dc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Distribution center not found"
        )
    
    await db.delete(dc)
    await db.commit()
