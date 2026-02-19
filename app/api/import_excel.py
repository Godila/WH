from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import time

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.excel_import import ExcelImportService
from app.schemas.import_schema import ExcelImportResponse, ExcelImportResult

router = APIRouter(prefix="/import", tags=["import"])

@router.post("/excel", response_model=ExcelImportResponse)
async def import_excel(
    file: UploadFile = File(..., description="Excel file with 'Сводная' sheet"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExcelImportResponse:
    """
    Import products from Excel file.
    """
    start_time = time.time()
    
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel format (.xlsx or .xls)")
    
    content = await file.read()
    service = ExcelImportService(db)
    result = await service.import_from_file(content)
    duration = time.time() - start_time
    
    return ExcelImportResponse(result=result, duration_seconds=round(duration, 2))
