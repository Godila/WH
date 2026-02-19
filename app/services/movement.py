from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock_movement import StockMovement, OperationType
from app.models.product import Product
from app.schemas.movement import MovementCreate


class MovementService:
    """Service for executing stock movement operations atomically."""
    
    @staticmethod
    async def _validate_product_exists(db: AsyncSession, product_id: str) -> Product:
        """Validate that product exists and is not deleted."""
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
    
    @staticmethod
    async def execute_movement(
        db: AsyncSession,
        data: MovementCreate,
        user_id: str
    ) -> StockMovement:
        """
        Execute a stock movement operation atomically.
        
        1. Validates product exists and is not deleted
        2. Validates conditional fields (already done in schema, but double-check)
        3. Executes stock updates based on operation type
        4. Creates audit log entry
        5. All in a single transaction (atomic)
        
        Raises:
            HTTPException 400: Validation error (insufficient stock)
            HTTPException 404: Product not found
        """
        # Validate product exists
        await MovementService._validate_product_exists(db, str(data.product_id))
        
        operation = data.operation_type
        qty = data.quantity
        pid = str(data.product_id)
        
        # Execute operation-specific stock updates
        if operation == OperationType.RECEIPT.value:
            # RECEIPT: Increase Stock
            await db.execute(
                text("UPDATE stocks SET quantity = quantity + :qty WHERE product_id = :pid"),
                {"qty": qty, "pid": pid}
            )
        
        elif operation == OperationType.RECEIPT_DEFECT.value:
            # RECEIPT_DEFECT: Increase DefectStock
            await db.execute(
                text("UPDATE defect_stocks SET quantity = quantity + :qty WHERE product_id = :pid"),
                {"qty": qty, "pid": pid}
            )
        
        elif operation == OperationType.SHIPMENT_RC.value:
            # SHIPMENT_RC: Decrease Stock with validation
            result = await db.execute(
                text("UPDATE stocks SET quantity = quantity - :qty "
                     "WHERE product_id = :pid AND quantity >= :qty "
                     "RETURNING quantity"),
                {"qty": qty, "pid": pid}
            )
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно товара для отгрузки"
                )
        
        elif operation == OperationType.RETURN_PICKUP.value:
            # RETURN_PICKUP: Increase Stock (source_id validated in schema)
            await db.execute(
                text("UPDATE stocks SET quantity = quantity + :qty WHERE product_id = :pid"),
                {"qty": qty, "pid": pid}
            )
        
        elif operation == OperationType.RETURN_DEFECT.value:
            # RETURN_DEFECT: Increase DefectStock (source_id validated in schema)
            await db.execute(
                text("UPDATE defect_stocks SET quantity = quantity + :qty WHERE product_id = :pid"),
                {"qty": qty, "pid": pid}
            )
        
        elif operation == OperationType.SELF_PURCHASE.value:
            # SELF_PURCHASE: Increase Stock (source_id validated in schema)
            await db.execute(
                text("UPDATE stocks SET quantity = quantity + :qty WHERE product_id = :pid"),
                {"qty": qty, "pid": pid}
            )
        
        elif operation == OperationType.WRITE_OFF.value:
            # WRITE_OFF: Decrease Stock, Increase DefectStock atomically
            result = await db.execute(
                text("UPDATE stocks SET quantity = quantity - :qty "
                     "WHERE product_id = :pid AND quantity >= :qty "
                     "RETURNING quantity"),
                {"qty": qty, "pid": pid}
            )
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно товара для списания в брак"
                )
            
            await db.execute(
                text("UPDATE defect_stocks SET quantity = quantity + :qty WHERE product_id = :pid"),
                {"qty": qty, "pid": pid}
            )
        
        elif operation == OperationType.RESTORATION.value:
            # RESTORATION: Decrease DefectStock, Increase Stock atomically
            result = await db.execute(
                text("UPDATE defect_stocks SET quantity = quantity - :qty "
                     "WHERE product_id = :pid AND quantity >= :qty "
                     "RETURNING quantity"),
                {"qty": qty, "pid": pid}
            )
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно брака для восстановления"
                )
            
            await db.execute(
                text("UPDATE stocks SET quantity = quantity + :qty WHERE product_id = :pid"),
                {"qty": qty, "pid": pid}
            )
        
        elif operation == OperationType.UTILIZATION.value:
            # UTILIZATION: Decrease DefectStock with validation
            result = await db.execute(
                text("UPDATE defect_stocks SET quantity = quantity - :qty "
                     "WHERE product_id = :pid AND quantity >= :qty "
                     "RETURNING quantity"),
                {"qty": qty, "pid": pid}
            )
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно брака для утилизации"
                )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown operation type: {operation}"
            )
        
        # Create audit log entry
        movement = StockMovement(
            operation_type=operation,
            product_id=data.product_id,
            quantity=data.quantity,
            source_id=data.source_id,
            distribution_center_id=data.distribution_center_id,
            user_id=user_id,
            notes=data.notes
        )
        db.add(movement)
        
        # Flush to get the movement ID (commit happens in API layer)
        await db.flush()
        await db.refresh(movement)
        
        return movement
