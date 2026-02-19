from typing import Optional

from pydantic import BaseModel, field_validator


class ExcelImportRow(BaseModel):
    """Schema representing one row from Excel import."""

    barcode: str
    seller_sku: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    stock_quantity: int = 0
    defect_quantity: int = 0
    row_number: int

    @field_validator("barcode", "seller_sku", "size", "brand", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class ExcelImportError(BaseModel):
    """Schema representing a validation error during import."""

    row_number: int
    field: str
    message: str


class ExcelImportResult(BaseModel):
    """Schema representing import summary."""

    total_rows: int
    created: int
    updated: int
    errors: list[ExcelImportError]
    success: bool


class ExcelImportResponse(BaseModel):
    """Schema for Excel import API response."""

    result: ExcelImportResult
    duration_seconds: float
