# Phase 04-03: Excel Import API Endpoint

## Summary
Created Excel import REST API endpoint with file upload handling and registered it in the FastAPI application.

## Changes
- **New file**: `app/api/import_excel.py` - Import router with POST /import/excel endpoint
- **Modified**: `app/main.py` - Registered import_excel router

## Implementation Details

### Endpoint: POST /api/import/excel
- **Authentication**: Protected by JWT (get_current_user dependency)
- **File validation**: Requires .xlsx or .xls extension
- **Request**: Multipart form with file upload
- **Response**: ExcelImportResponse with result and duration_seconds

### Key Features
1. FastAPI UploadFile handling with File(...)
2. File extension validation (.xlsx, .xls)
3. Delegates parsing to ExcelImportService
4. Returns structured response with timing info
5. JWT authentication protection

## Commits
```
a068235 feat(04-excel-import-03): create import API endpoint
760f0ad feat(04-excel-import-03): register import router in main.py
```

## Success Criteria Status
- [x] Manager can POST Excel file to /api/import/excel
- [x] File must have "Сводная" sheet (handled by service)
- [x] New products created when barcode doesn't exist (handled by service)
- [x] Existing products updated when barcode exists (handled by service)
- [x] Stock.quantity updated from "АКТУАЛЬНЫЙ ОСТАТОК" (handled by service)
- [x] DefectStock.quantity updated from "БРАКИ" (handled by service)
- [x] Response includes created/updated counts and errors
