from uuid import UUID
import math

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.product import Product
from app.models.stock import Stock
from app.models.defect_stock import DefectStock
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithStockResponse,
    ProductListResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    barcode: str | None = Query(None, description="Search by barcode"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductListResponse:
    """
    List products with pagination and optional barcode search.
    
    - Excludes soft-deleted products
    - Includes stock_quantity and defect_quantity
    """
    # Base query - exclude deleted
    base_query = select(Product).where(Product.is_deleted == False)
    
    # Barcode search filter
    if barcode:
        base_query = base_query.where(Product.barcode.ilike(f"%{barcode}%"))
    
    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Calculate pagination
    offset = (page - 1) * page_size
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Fetch products with stock data
    query = (
        base_query
        .options(selectinload(Product.stock), selectinload(Product.defect_stock))
        .order_by(Product.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    products = list(result.scalars().all())
    
    # Build response with stock quantities
    items = []
    for product in products:
        stock_qty = product.stock.quantity if product.stock else 0
        defect_qty = product.defect_stock.quantity if product.defect_stock else 0
        
        items.append(ProductWithStockResponse(
            id=product.id,
            barcode=product.barcode,
            gtin=product.gtin,
            seller_sku=product.seller_sku,
            size=product.size,
            brand=product.brand,
            color=product.color,
            created_at=product.created_at,
            updated_at=product.updated_at,
            stock_quantity=stock_qty,
            defect_quantity=defect_qty,
        ))
    
    return ProductListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Product:
    """
    Create a new product with auto-created Stock and DefectStock records.
    
    - Validates barcode uniqueness
    - Validates GTIN uniqueness
    - Creates Stock with quantity=0
    - Creates DefectStock with quantity=0
    """
    # Check barcode uniqueness
    existing_barcode = await db.execute(
        select(Product).where(Product.barcode == data.barcode)
    )
    if existing_barcode.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with barcode '{data.barcode}' already exists"
        )
    
    # Check GTIN uniqueness
    existing_gtin = await db.execute(
        select(Product).where(Product.gtin == data.gtin)
    )
    if existing_gtin.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with GTIN '{data.gtin}' already exists"
        )
    
    # Create product
    product = Product(
        barcode=data.barcode,
        gtin=data.gtin,
        seller_sku=data.seller_sku,
        size=data.size,
        brand=data.brand,
        color=data.color,
    )
    db.add(product)
    await db.flush()  # Get the product ID
    
    # Create Stock record
    stock = Stock(product_id=product.id, quantity=0)
    db.add(stock)
    
    # Create DefectStock record
    defect_stock = DefectStock(product_id=product.id, quantity=0)
    db.add(defect_stock)
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Product:
    """
    Get a product by ID.
    
    - Returns 404 if product not found or is deleted
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.is_deleted == False
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Product:
    """
    Update a product (partial update).
    
    - Validates barcode uniqueness if being updated
    - Validates GTIN uniqueness if being updated
    - Returns 404 if product not found or is deleted
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.is_deleted == False
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Check barcode uniqueness if being updated
    if "barcode" in update_data and update_data["barcode"] != product.barcode:
        existing = await db.execute(
            select(Product).where(Product.barcode == update_data["barcode"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with barcode '{update_data['barcode']}' already exists"
            )
    
    # Check GTIN uniqueness if being updated
    if "gtin" in update_data and update_data["gtin"] != product.gtin:
        existing = await db.execute(
            select(Product).where(Product.gtin == update_data["gtin"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with GTIN '{update_data['gtin']}' already exists"
            )
    
    # Update fields
    for key, value in update_data.items():
        setattr(product, key, value)
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Soft delete a product.
    
    - Sets is_deleted=True
    - Returns 404 if product not found or already deleted
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.is_deleted == False
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_deleted = True
    await db.commit()
