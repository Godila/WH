import math
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.stock_movement import StockMovement
from app.models.product import Product
from app.models.stock import Stock
from app.models.defect_stock import DefectStock
from app.schemas.movement import (
    MovementCreate,
    MovementResponse,
    MovementFilter,
    MovementListResponse,
)
from app.services.movement import MovementService
from app.api.deps import get_current_user

router = APIRouter(prefix="/stock", tags=["stock"])


@router.post("/movements", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
    data: MovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MovementResponse:
    """
    Execute a stock movement operation.
    
    - Validates product exists
    - Validates conditional fields (source_id, distribution_center_id)
    - Updates stock atomically
    - Creates audit log entry
    
    Returns 400 if insufficient stock for the operation.
    """
    movement = await MovementService.execute_movement(
        db=db,
        data=data,
        user_id=str(current_user.id)
    )
    await db.commit()
    await db.refresh(movement)
    
    # Load relationships for response
    await db.refresh(movement, ["product"])
    
    return MovementResponse(
        id=movement.id,
        operation_type=movement.operation_type,
        product_id=movement.product_id,
        quantity=movement.quantity,
        source_id=movement.source_id,
        distribution_center_id=movement.distribution_center_id,
        user_id=movement.user_id,
        notes=movement.notes,
        created_at=movement.created_at,
        product_barcode=movement.product.barcode,
        product_gtin=movement.product.gtin,
    )


@router.get("/movements", response_model=MovementListResponse)
async def list_movements(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    operation_type: str | None = Query(None, description="Filter by operation type"),
    product_id: UUID | None = Query(None, description="Filter by product"),
    date_from: datetime | None = Query(None, description="Filter from date"),
    date_to: datetime | None = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MovementListResponse:
    """
    List stock movement journal with filtering and pagination.
    
    - Filter by operation_type, product_id, date range
    - Sorted by created_at DESC (newest first)
    - Includes product barcode and GTIN for display
    """
    # Base query with product relationship
    base_query = (
        select(StockMovement)
        .options(selectinload(StockMovement.product))
    )
    
    # Apply filters
    if operation_type:
        base_query = base_query.where(StockMovement.operation_type == operation_type)
    
    if product_id:
        base_query = base_query.where(StockMovement.product_id == product_id)
    
    if date_from:
        base_query = base_query.where(StockMovement.created_at >= date_from)
    
    if date_to:
        base_query = base_query.where(StockMovement.created_at <= date_to)
    
    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Calculate pagination
    offset = (page - 1) * page_size
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Fetch movements with pagination
    query = (
        base_query
        .order_by(StockMovement.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    movements = list(result.scalars().all())
    
    # Build response items
    items = []
    for movement in movements:
        items.append(MovementResponse(
            id=movement.id,
            operation_type=movement.operation_type,
            product_id=movement.product_id,
            quantity=movement.quantity,
            source_id=movement.source_id,
            distribution_center_id=movement.distribution_center_id,
            user_id=movement.user_id,
            notes=movement.notes,
            created_at=movement.created_at,
            product_barcode=movement.product.barcode if movement.product else None,
            product_gtin=movement.product.gtin if movement.product else None,
        ))
    
    return MovementListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/summary")
async def get_stock_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get stock summary statistics.
    
    Returns:
        - total_products: Count of non-deleted products
        - total_stock: Sum of all Stock quantities
        - total_defect: Sum of all DefectStock quantities
    """
    # Count non-deleted products
    product_count = await db.execute(
        select(func.count()).select_from(Product).where(Product.is_deleted == False)
    )
    total_products = product_count.scalar() or 0
    
    # Sum all stock quantities
    stock_sum = await db.execute(
        select(func.coalesce(func.sum(Stock.quantity), 0))
    )
    total_stock = stock_sum.scalar() or 0
    
    # Sum all defect quantities
    defect_sum = await db.execute(
        select(func.coalesce(func.sum(DefectStock.quantity), 0))
    )
    total_defect = defect_sum.scalar() or 0
    
    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "total_defect": total_defect,
    }
