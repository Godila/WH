# Phase 04-02: ExcelImportService with Parsing

## Summary
Created `ExcelImportService` class in `app/services/excel_import.py` with full parsing, validation, and batch upsert logic for Excel imports.

## Changes
- **New file**: `app/services/excel_import.py`
- **Modified**: `app/services/__init__.py` (exported ExcelImportService)

## Implementation Details

### Column Mapping (Russian → English)
| Excel Column | Field |
|--------------|-------|
| Баркод | barcode |
| Артикул продавца | seller_sku |
| Размер | size |
| Бренд | brand |
| АКТУАЛЬНЫЙ ОСТАТОК | stock_quantity |
| БРАКИ | defect_quantity |

### Key Features
1. **Memory-efficient parsing**: Uses `openpyxl` with `read_only=True` for streaming large files
2. **Sheet finding**: Automatically finds sheet named "Сводная"
3. **Validation before write**: Validates ALL rows before ANY database write
4. **Batch processing**: Processes 500 rows per transaction
5. **GTIN generation**: 
   - Uses barcode as GTIN if 13-14 digits (padded to 14)
   - Otherwise generates "IMP" + barcode padded to 14 chars
6. **Empty cell handling**: Treats None/empty as 0 for numeric fields
7. **Duplicate detection**: Checks for duplicate barcodes in single import
8. **Atomic upsert**: Updates existing products or creates new ones with Stock and DefectStock

### Methods
- `parse_excel(file_content)` - Parse Excel, return rows and parse errors
- `validate_rows(rows)` - Validate all rows, return errors (no DB writes)
- `import_batch(rows)` - Import batch of 500 validated rows
- `import_from_file(file_content)` - Main entry point

## Commit
```
a67a0bf feat(04-excel-import-02): create excel-import-service-with-parsing
```
