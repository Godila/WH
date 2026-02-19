# Plan 03-01-SUMMARY: Data Layer

**Status:** Complete
**Completed:** 2026-02-19
**Commits:** 1

## What Was Built

### Models
- **OperationType enum** (`app/models/stock_movement.py`):
  - 9 operation types: RECEIPT, RECEIPT_DEFECT, SHIPMENT_RC, RETURN_PICKUP, RETURN_DEFECT, SELF_PURCHASE, WRITE_OFF, RESTORATION, UTILIZATION
  - str enum for easy serialization

- **StockMovement model** (`app/models/stock_movement.py`):
  - operation_type (String 50, indexed)
  - product_id (FK to products, indexed)
  - quantity (Integer)
  - source_id (nullable FK to sources)
  - distribution_center_id (nullable FK to distribution_centers)
  - user_id (FK to users, indexed)
  - notes (Text, nullable)
  - Relationships to Product, Source, DistributionCenter, User

- **Updated models** for back-references:
  - Product.movements
  - Source.movements
  - DistributionCenter.movements
  - User.movements

### Schemas
- **app/schemas/movement.py**:
  - MovementBase: product_id, operation_type, quantity (validated ge=1), source_id, distribution_center_id, notes
  - MovementCreate: extends MovementBase with model_validator for conditional fields
    - source_id required for RETURN_PICKUP, RETURN_DEFECT, SELF_PURCHASE
    - distribution_center_id required for SHIPMENT_RC
  - MovementResponse: includes id, user_id, created_at, product_barcode, product_gtin
  - MovementFilter: operation_type, product_id, date_from, date_to
  - MovementListResponse: paginated list with metadata

### Migration
- **alembic/versions/003_stock_movements.py**:
  - Creates stock_movements table
  - FKs with proper ondelete (CASCADE for product/user, SET NULL for source/dc)
  - Indexes on product_id, operation_type, created_at, user_id

## Files Created/Modified

| File | Purpose |
|------|---------|
| app/models/stock_movement.py | StockMovement model + OperationType enum |
| app/models/__init__.py | Export StockMovement, OperationType |
| app/models/product.py | Add movements relationship |
| app/models/source.py | Add movements relationship |
| app/models/distribution_center.py | Add movements relationship |
| app/models/user.py | Add movements relationship |
| app/schemas/movement.py | Movement Pydantic schemas |
| alembic/versions/003_stock_movements.py | Migration for stock_movements |

## Must-Haves Verified

- [x] StockMovement model stores operation type, quantity, product, optional source/dc
- [x] OperationType enum defines all 9 operation types
- [x] Migration creates stock_movements table with proper indexes
- [x] Schemas define request/response shapes for movement operations

## Next Steps

Plan 03-02 will build on this foundation:
- MovementService with 9 operation handlers
- Atomic stock updates with TOCTOU protection
- Validation and audit logging
