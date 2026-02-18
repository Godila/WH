# Project Research Summary

**Project:** WMS / Marketplace Fulfillment System
**Domain:** Warehouse Management System / Fulfillment
**Researched:** 2026-02-18
**Confidence:** MEDIUM-HIGH

## Executive Summary

This is a Warehouse Management System (WMS) for Russian marketplace fulfillment operations. Expert-built WMS systems follow a layered architecture pattern where stock operations are always atomic, audit trails are immutable, and business logic lives in a dedicated service layer separate from API handlers. The system must handle 9 distinct operation types (receipts, shipments, returns, defects, write-offs) across 2 warehouses (Stock and DefectStock) for 2-3 users.

The recommended approach is a **monolithic FastAPI backend with async SQLAlchemy** paired with a **React + Ant Design frontend**. This stack provides the right balance of developer productivity, performance, and enterprise-grade UI components. The critical architectural decision is the **Service layer pattern** — all stock operations must flow through a `MovementService` that validates stock sufficiency, updates balances, and logs audit events in a single atomic transaction.

Key risks center on **concurrent inventory modifications** (race conditions causing negative stock) and **Excel import data corruption**. Both are mitigated through atomic database operations with conditional updates and strict server-side validation schemas. Do not skip the Service layer or bypass transactions — this is how WMS systems fail in production.

## Key Findings

### Recommended Stack

Python async backend with PostgreSQL, React SPA frontend with Ant Design components. All database operations use SQLAlchemy 2.0's native async support.

**Core technologies:**
- **FastAPI 0.129.0** — Async REST framework with auto-generated OpenAPI docs
- **SQLAlchemy 2.0.46** — Only production-ready async ORM for Python; Unit of Work pattern
- **PostgreSQL 16** — ACID compliance for inventory; JSONB for flexible attributes
- **React 18 + Ant Design 6** — Enterprise-grade UI components; Russian locale support
- **Zustand 5** — State management with 90% less boilerplate than Redux
- **python-jose + passlib** — JWT auth with bcrypt password hashing

### Expected Features

**Must have (table stakes) — MVP:**
- User Authentication (JWT, 2 roles: admin/operator)
- Multi-Warehouse (Stock + DefectStock)
- 9 Operation Types (RECEIPT, RECEIPT_DEFECT, RETURN_PICKUP, RETURN_DEFECT, SHIPMENT_RC, SELF_PURCHASE, WRITE_OFF, RESTORATION, UTILIZATION)
- Movement Journal with filtering
- Stock Balances per warehouse
- SKU Management

**Should have (differentiators) — v1.x:**
- Excel Import/Export — bulk data entry and reporting
- SKU Search/Filter — essential as inventory grows
- Stock Alerts (low stock notifications)
- Basic Dashboard — KPIs and visibility

**Defer (v2+):**
- Barcode/QR Scanning — requires mobile interface
- Marketplace API Integration — Ozon, WB sync (high complexity)
- Mobile PWA — significant UI investment
- Advanced Analytics — needs data accumulation

### Architecture Approach

**Layered architecture:** API handlers → Service layer (business logic) → Repository/CRUD (data access). The Service layer is non-negotiable for WMS — stock validation, operation orchestration, and audit logging must never live in API handlers.

**Major components:**
1. **MovementService** — Orchestrates all 9 operation types with validation, stock updates, and audit logging in atomic transactions
2. **StockService** — Balance calculations, stock sufficiency validation, concurrent access handling
3. **AuditService** — Immutable event logging for compliance and debugging
4. **Frontend services/hooks** — Axios API client with Zustand for user state, React Query for server state caching

### Critical Pitfalls

1. **TOCTOU Race Condition** — Two operations check stock simultaneously, both see sufficient quantity, both decrement → negative inventory. Prevent with atomic `UPDATE ... WHERE quantity >= required` or optimistic locking with version field.

2. **Partial Operation Failure** — Movement created but stock not updated (or vice versa). ALL related operations must be in a single transaction; never commit partial state.

3. **Excel Import Memory Exhaustion** — Loading 10K+ rows into memory crashes. Use streaming API and batch processing (500-1000 rows per transaction).

4. **Silent Excel Data Corruption** — Leading zeros stripped from SKUs, dates shift, numbers become strings. Strict server-side validation with Zod schemas; validate ALL rows before ANY database write.

5. **Missing Idempotency** — Double-click or network retry duplicates operations. Require idempotency keys for mutating operations; cache results for replay.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation & Authentication
**Rationale:** No dependencies; everything else requires users and database. Must establish transaction patterns from day one.
**Delivers:** PostgreSQL database, async engine, User model, JWT auth, basic CRUD patterns
**Addresses:** User Authentication
**Avoids:** Partial operation failure (transaction patterns established early)

### Phase 2: Master Data & Warehouses
**Rationale:** Products, Sources, Distribution Centers are referenced by all stock operations. These are foundational master data.
**Delivers:** Product/SKU management, Source (suppliers), Distribution Center management, basic frontend pages
**Addresses:** SKU Management, Multi-Warehouse setup
**Uses:** SQLAlchemy 2.0 models, Alembic migrations

### Phase 3: Stock Core & Operations
**Rationale:** Stock and StockMovements depend on Products and DCs. This is the heart of the WMS — all 9 operation types implemented here.
**Delivers:** Stock model, MovementService with all 9 operation types, stock validation, balance updates, Movement Journal
**Addresses:** Stock Receipt, Stock Shipment, Return Handling, Defect Operations, Movement Journal, Stock Balances
**Avoids:** TOCTOU race condition (atomic operations), Ambiguous operation effects (single source of truth)
**Implements:** Service layer pattern, Unit of Work, Optimistic locking

### Phase 4: Defect Management
**Rationale:** DefectStock depends on StockMovements; separate concerns for clarity.
**Delivers:** DefectStock model, defect-specific operations, frontend Defects page
**Addresses:** Defect/Write-off operations
**Uses:** Stock movement infrastructure from Phase 3

### Phase 5: Audit & Reporting
**Rationale:** AuditLog captures events from all operations; best added after core operations are stable.
**Delivers:** AuditService, immutable event logging, basic reports/export
**Addresses:** Audit trail, Basic Reports
**Avoids:** Missing audit trail (append-only logs from start)

### Phase 6: Excel Import/Export (v1.x)
**Rationale:** Bulk operations require stable core; import is high-risk feature best added after validation.
**Delivers:** Excel import with streaming, row validation, error reporting; Excel export for reports
**Addresses:** Excel Import, Excel Export
**Avoids:** Excel memory exhaustion (streaming), Silent data corruption (validation), Lost update problem (optimistic locking)
**Uses:** openpyxl library

### Phase Ordering Rationale

- **Foundation first:** Users and database are prerequisites for everything
- **Master data before transactions:** Products/DCs must exist before stock operations
- **Stock operations before audit:** Core value first, observability second
- **Excel last:** High-risk feature; needs stable foundation and thorough validation

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Stock Operations):** Complex business logic for 9 operation types; may need domain expert validation on operation semantics
- **Phase 6 (Excel Import):** File format edge cases; streaming patterns need verification with actual data volumes

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundation):** FastAPI + SQLAlchemy patterns are well-documented
- **Phase 2 (Master Data):** Basic CRUD, no special complexity
- **Phase 5 (Audit):** Standard event logging pattern

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified via PyPI/npm; patterns verified via Context7 official docs |
| Features | MEDIUM | Based on Wikipedia WMS article, ERPNext docs, and domain knowledge; some assumptions about Russian marketplace specifics |
| Architecture | HIGH | FastAPI/SQLAlchemy patterns verified; layered architecture is standard for enterprise apps |
| Pitfalls | MEDIUM | Database patterns HIGH confidence (PostgreSQL docs); Excel patterns HIGH (ExcelJS docs); domain-specific pitfalls from industry experience |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Russian marketplace specifics:** Ozon, WB, Yandex Market API behaviors not deeply researched; defer integration research to Phase 3+ when API integration is scoped
- **Barcode scanning implementation:** Deferred to v2; needs hardware/scope clarification before research
- **Multi-currency handling:** Mentioned as differentiator but not detailed; may need research if prioritized
- **2-3 user scale validation:** Architecture assumes small scale; if user count grows, revisit scaling considerations

## Sources

### Primary (HIGH confidence)
- Context7 `/fastapi/fastapi` — FastAPI installation, dependency injection, project structure
- Context7 `/websites/sqlalchemy_en_21` — SQLAlchemy 2.0 async patterns, Unit of Work
- Context7 `/pmndrs/zustand` — Zustand v5 TypeScript patterns
- Context7 `/websites/ant_design` — Ant Design 6 installation, components
- PostgreSQL Transaction Isolation Documentation — Isolation levels, race conditions
- Prisma Transaction Documentation — Transaction patterns, batch operations

### Secondary (MEDIUM confidence)
- Wikipedia WMS Article — WMS complexity levels, core functions
- ERPNext Stock Module Documentation — Practical WMS implementation reference
- Martin Fowler: Patterns of Enterprise Architecture — Unit of Work, Repository, Domain Events
- ExcelJS Documentation (Context7) — Streaming API for large files
- Baeldung: Race Conditions in Distributed Systems — TOCTOU prevention

### Tertiary (LOW confidence)
- Domain knowledge (industry experience) — WMS operation types, fulfillment patterns
- Project context from orchestrator — Specific 9 operation types, 2 warehouse structure

---
*Research completed: 2026-02-18*
*Ready for roadmap: yes*
