# Plan 03-02-SUMMARY: Service Layer

**Status:** Complete
**Completed:** 2026-02-19
**Commits:** 1

## What Was Built

### MovementService
- **app/services/movement.py**: Core business logic for stock operations

**9 Operation Handlers:**

| Operation | Stock Effect | DefectStock Effect | Validation |
|-----------|--------------|-------------------|------------|
| RECEIPT | +qty | - | None |
| RECEIPT_DEFECT | - | +qty | None |
| SHIPMENT_RC | -qty | - | Stock >= qty |
| RETURN_PICKUP | +qty | - | source_id required |
| RETURN_DEFECT | - | +qty | source_id required |
| SELF_PURCHASE | +qty | - | source_id required |
| WRITE_OFF | -qty | +qty | Stock >= qty |
| RESTORATION | +qty | -qty | DefectStock >= qty |
| UTILIZATION | - | -qty | DefectStock >= qty |

### Key Design Decisions

1. **TOCTOU Prevention**: All stock decreases use raw SQL:
   ```sql
   UPDATE stocks SET quantity = quantity - :qty 
   WHERE product_id = :pid AND quantity >= :qty
   ```
   This prevents race conditions where two operations might both see sufficient stock and both decrease.

2. **Atomic Operations**: WRITE_OFF and RESTORATION update both tables in a single transaction - either both succeed or both fail.

3. **Audit Logging**: Every operation creates a StockMovement record for compliance.

4. **Russian Error Messages**:
   - "Недостаточно товара для отгрузки"
   - "Недостаточно товара для списания в брак"
   - "Недостаточно брака для восстановления"
   - "Недостаточно брака для утилизации"

## Files Created/Modified

| File | Purpose |
|------|---------|
| app/services/movement.py | MovementService with 9 operations |
| app/services/__init__.py | Export MovementService |

## Must-Haves Verified

- [x] RECEIPT operation increases Stock.quantity
- [x] RECEIPT_DEFECT operation increases DefectStock.quantity
- [x] SHIPMENT_RC decreases Stock.quantity and fails if insufficient stock
- [x] RETURN_PICKUP increases Stock.quantity (requires source_id)
- [x] RETURN_DEFECT increases DefectStock.quantity (requires source_id)
- [x] SELF_PURCHASE increases Stock.quantity (requires source_id)
- [x] WRITE_OFF decreases Stock and increases DefectStock atomically
- [x] RESTORATION decreases DefectStock and increases Stock atomically
- [x] UTILIZATION decreases DefectStock and fails if insufficient defect stock
- [x] All operations are atomic - either all updates happen or none
- [x] All operations create StockMovement audit log entry

## Next Steps

Plan 03-03 will build on this foundation:
- REST API endpoints for movements
- Journal filtering and pagination
- Stock summary endpoint
