from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    """Base schema for Product."""
    barcode: str
    gtin: str
    seller_sku: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a Product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a Product (partial updates)."""
    barcode: Optional[str] = None
    gtin: Optional[str] = None
    seller_sku: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None


class ProductResponse(ProductBase):
    """Schema for Product response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductWithStockResponse(ProductResponse):
    """Schema for Product response with stock quantities."""
    stock_quantity: int
    defect_quantity: int

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    items: list[ProductWithStockResponse]
    total: int
    page: int
    page_size: int
    pages: int

    class Config:
        from_attributes = True
