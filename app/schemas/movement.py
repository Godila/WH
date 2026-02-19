from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self


class MovementBase(BaseModel):
    """Base schema for stock movement."""
    product_id: UUID
    operation_type: str
    quantity: int  # ge=1 validation in model_validator
    source_id: Optional[UUID] = None
    distribution_center_id: Optional[UUID] = None
    notes: Optional[str] = None

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        return v

    @field_validator('operation_type')
    @classmethod
    def validate_operation_type(cls, v: str) -> str:
        valid_types = [
            'receipt', 'receipt_defect', 'shipment_rc',
            'return_pickup', 'return_defect', 'self_purchase',
            'write_off', 'restoration', 'utilization'
        ]
        if v not in valid_types:
            raise ValueError(f'Invalid operation_type. Must be one of: {valid_types}')
        return v


class MovementCreate(MovementBase):
    """Schema for creating a stock movement."""
    
    @model_validator(mode='after')
    def validate_conditional_fields(self) -> Self:
        """Validate that conditional fields are present based on operation type."""
        # source_id is required for RETURN_* and SELF_PURCHASE
        source_required_ops = ['return_pickup', 'return_defect', 'self_purchase']
        if self.operation_type in source_required_ops and not self.source_id:
            raise ValueError(
                f'source_id is required for operation_type: {self.operation_type}'
            )
        
        # distribution_center_id is required for SHIPMENT_RC
        if self.operation_type == 'shipment_rc' and not self.distribution_center_id:
            raise ValueError(
                'distribution_center_id is required for operation_type: shipment_rc'
            )
        
        return self


class MovementResponse(MovementBase):
    """Schema for stock movement response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    product_barcode: Optional[str] = None
    product_gtin: Optional[str] = None

    class Config:
        from_attributes = True


class MovementFilter(BaseModel):
    """Schema for filtering movement journal."""
    operation_type: Optional[str] = None
    product_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class MovementListResponse(BaseModel):
    """Schema for paginated movement list response."""
    items: list[MovementResponse]
    total: int
    page: int
    page_size: int
    pages: int

    class Config:
        from_attributes = True
