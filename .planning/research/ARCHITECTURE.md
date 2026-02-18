# Architecture Research: WMS/Fulfillment System

**Domain:** Warehouse Management System / Fulfillment
**Researched:** 2026-02-18
**Confidence:** HIGH (FastAPI/SQLAlchemy patterns verified via Context7, WMS domain patterns from enterprise architecture literature)

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Products   │  │    Stock    │  │  Operations │  │   Reports   │    │
│  │   Pages     │  │   Pages     │  │   Pages     │  │   Pages     │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐    │
│  │              Ant Design Components + React Query               │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────────────┐
│                            API LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Products   │  │    Stock    │  │ Movements   │  │    Users    │    │
│  │  Router     │  │   Router    │  │   Router    │  │   Router    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐    │
│  │         FastAPI Dependencies (Auth, DB Session, Validation)    │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          SERVICE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Product   │  │    Stock    │  │  Movement   │  │    Audit    │    │
│  │   Service   │  │   Service   │  │   Service   │  │   Service   │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐    │
│  │              Business Logic + Domain Events                    │    │
│  │        (Stock validation, Balance calculations, Rules)         │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          REPOSITORY LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Product   │  │    Stock    │  │  Movement   │  │     DC      │    │
│  │   CRUD      │  │    CRUD     │  │    CRUD     │  │    CRUD     │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐    │
│  │              Unit of Work + AsyncSession Management            │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ products │  │  stock   │  │defect_   │  │ stock_   │  │  users   │  │
│  │          │  │          │  │ stock    │  │movements │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                               │
│  │ sources  │  │dist_     │  │ audit_   │  ← PostgreSQL + AsyncPG       │
│  │          │  │centers   │  │  log     │                               │
│  └──────────┘  └──────────┘  └──────────┘                               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **API Routers** | HTTP endpoint definitions, request/response schemas, route-level validation | FastAPI `APIRouter` with Pydantic schemas |
| **Dependencies** | Auth, DB session injection, shared parameters | FastAPI `Depends()` with `Annotated` |
| **Services** | Business logic, stock validation, operation orchestration, domain events | Python classes with async methods |
| **Repositories/CRUD** | Database operations, queries, data access abstraction | SQLAlchemy 2.0 async patterns |
| **Models** | ORM definitions, table mappings, relationships | SQLAlchemy declarative models |
| **Schemas** | Input validation, output serialization, API contracts | Pydantic v2 models |

## Recommended Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (env vars, secrets)
│   │   ├── database.py            # Async engine, sessionmaker
│   │   ├── dependencies.py        # Common deps (get_db, get_current_user)
│   │   └── security.py            # JWT, password hashing
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                # Base model class, mixins
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── stock.py
│   │   ├── stock_movement.py
│   │   ├── defect_stock.py
│   │   ├── source.py
│   │   ├── distribution_center.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py                # UserCreate, UserRead, UserUpdate
│   │   ├── product.py
│   │   ├── stock.py
│   │   ├── stock_movement.py      # MovementCreate, MovementRead
│   │   ├── defect_stock.py
│   │   ├── source.py
│   │   ├── distribution_center.py
│   │   └── common.py              # Pagination, common types
│   │
│   ├── crud/                      # Repository layer
│   │   ├── __init__.py
│   │   ├── base.py                # Generic CRUD base class
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── stock.py
│   │   ├── stock_movement.py
│   │   ├── defect_stock.py
│   │   ├── source.py
│   │   └── distribution_center.py
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── stock_service.py       # Stock balance calculations
│   │   ├── movement_service.py    # 9 operation types orchestration
│   │   ├── product_service.py
│   │   ├── audit_service.py       # Domain events logging
│   │   └── validation_service.py  # Stock sufficiency validation
│   │
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Route-specific deps
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Aggregates all v1 routers
│   │       ├── auth.py            # Login, logout
│   │       ├── users.py
│   │       ├── products.py
│   │       ├── stock.py
│   │       ├── stock_movements.py
│   │       ├── defect_stock.py
│   │       ├── sources.py
│   │       └── distribution_centers.py
│   │
│   └── utils/                     # Helper functions
│       ├── __init__.py
│       └── pagination.py
│
├── migrations/                    # Alembic migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
│
├── alembic.ini
├── pyproject.toml
└── .env
```

```
frontend/
├── src/
│   ├── assets/                    # Static resources
│   ├── components/                # Shared UI components
│   │   ├── Layout/
│   │   │   ├── index.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── StockTable/
│   │   ├── MovementForm/
│   │   └── common/               # Buttons, modals, etc.
│   │
│   ├── pages/                     # Route pages
│   │   ├── Dashboard/
│   │   ├── Products/
│   │   │   ├── index.tsx
│   │   │   ├── ProductForm.tsx
│   │   │   └── components/
│   │   ├── Stock/
│   │   ├── Movements/
│   │   │   ├── index.tsx
│   │   │   ├── MovementCreate.tsx
│   │   │   └── components/
│   │   ├── DefectStock/
│   │   ├── Sources/
│   │   ├── DistributionCenters/
│   │   └── Users/
│   │
│   ├── services/                  # API client
│   │   ├── api.ts                # Axios/fetch wrapper
│   │   ├── products.ts
│   │   ├── stock.ts
│   │   ├── movements.ts
│   │   └── auth.ts
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useProducts.ts
│   │   ├── useStock.ts
│   │   └── useMovements.ts
│   │
│   ├── stores/                    # State management
│   │   └── userStore.ts
│   │
│   ├── utils/                     # Helper functions
│   ├── types/                     # TypeScript types
│   ├── App.tsx
│   └── main.tsx
│
├── package.json
└── vite.config.ts
```

### Structure Rationale

- **`models/` vs `schemas/` separation:** Models are database representations; schemas are API contracts. This prevents leaking internal DB structure to API consumers.
- **`services/` layer:** Critical for WMS — business logic (stock validation, operation rules) should not live in API handlers or CRUD.
- **`crud/` as repositories:** Encapsulates all SQLAlchemy queries. Makes testing easier (can mock CRUD layer).
- **`api/v1/` versioning:** WMS APIs evolve; version from day one.
- **Frontend `services/` + `hooks/` separation:** Services handle HTTP; hooks handle React Query/state.

## Architectural Patterns

### Pattern 1: Layered Architecture (API → Service → Repository)

**What:** Requests flow through distinct layers: API handles HTTP → Service enforces business rules → Repository accesses data.

**When to use:** Always for WMS. Business logic (stock validation, operation rules) is too complex for controllers.

**Trade-offs:**
- (+) Clear separation of concerns
- (+) Testable at each layer
- (-) More boilerplate for simple CRUD
- (-) Can feel over-engineered early

**Example:**
```python
# api/v1/stock_movements.py
@router.post("/movements/", response_schema=MovementRead)
async def create_movement(
    movement_in: MovementCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await movement_service.create_movement(
        session=session,
        movement_data=movement_in,
        user_id=current_user.id,
    )

# services/movement_service.py
class MovementService:
    async def create_movement(
        self,
        session: AsyncSession,
        movement_data: MovementCreate,
        user_id: int,
    ) -> StockMovement:
        # 1. Validate stock sufficiency
        await self._validate_stock(session, movement_data)
        
        # 2. Create movement record
        movement = await crud.stock_movement.create(session, movement_data)
        
        # 3. Update stock balance (in same transaction)
        await self._update_stock_balance(session, movement)
        
        # 4. Log audit event
        await self._log_audit(session, movement, user_id)
        
        return movement
```

### Pattern 2: Unit of Work with AsyncSession

**What:** SQLAlchemy session acts as Unit of Work — tracks changes and commits atomically.

**When to use:** All stock operations must be atomic. Never update stock without transaction.

**Trade-offs:**
- (+) Automatic change tracking
- (+) Atomic commits/rollbacks
- (-) Must manage session lifecycle carefully
- (-) Async requires explicit `await`

**Example:**
```python
# core/database.py
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()
            raise

# In service - multiple operations in one transaction
async def receive_stock(session: AsyncSession, data: ReceiveData):
    # All in one transaction
    product = await crud.product.get(session, data.product_id)
    stock = await crud.stock.get_by_product_dc(session, data.product_id, data.dc_id)
    
    stock.quantity += data.quantity  # Tracked by session
    
    movement = StockMovement(
        operation_type=OperationType.RECEIVE,
        quantity=data.quantity,
        # ...
    )
    session.add(movement)
    
    # Commit happens in get_db() middleware
```

### Pattern 3: Domain Events for Audit Trail

**What:** Every stock operation emits an immutable event logged for audit/debugging.

**When to use:** Required for WMS — you must know WHO changed WHAT and WHEN.

**Trade-offs:**
- (+) Complete audit trail
- (+) Enables event sourcing later
- (+) Debugging becomes trivial
- (-) More storage
- (-) Events are immutable (corrections need new events)

**Example:**
```python
# models/audit_log.py
class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str]  # "stock.receive", "stock.defect", etc.
    entity_type: Mapped[str]  # "stock", "product", etc.
    entity_id: Mapped[int]
    user_id: Mapped[int]
    occurred_at: Mapped[datetime]
    source_data: Mapped[dict] = mapped_column(JSON)  # Immutable event payload
    processing_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

# services/audit_service.py
class AuditService:
    async def log_event(
        self,
        session: AsyncSession,
        event_type: str,
        entity_type: str,
        entity_id: int,
        user_id: int,
        source_data: dict,
    ) -> AuditLog:
        log = AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            occurred_at=datetime.utcnow(),
            source_data=source_data,  # Immutable!
        )
        session.add(log)
        return log
```

### Pattern 4: Optimistic Locking for Stock Updates

**What:** Use version/timestamp column to detect concurrent modifications.

**When to use:** Multiple users may update same stock simultaneously.

**Trade-offs:**
- (+) No database locks
- (+) Handles concurrent access
- (-) Retry logic needed on conflicts
- (-) Slight complexity increase

**Example:**
```python
# models/stock.py
class Stock(Base):
    __tablename__ = "stock"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    dc_id: Mapped[int] = mapped_column(ForeignKey("distribution_centers.id"))
    quantity: Mapped[int] = mapped_column(default=0)
    version: Mapped[int] = mapped_column(default=1)  # Optimistic lock

# crud/stock.py
async def update_quantity(
    self,
    session: AsyncSession,
    stock_id: int,
    delta: int,
    expected_version: int,
) -> Stock:
    stmt = (
        update(Stock)
        .where(Stock.id == stock_id, Stock.version == expected_version)
        .values(quantity=Stock.quantity + delta, version=Stock.version + 1)
        .returning(Stock)
    )
    result = await session.execute(stmt)
    stock = result.scalar_one_or_none()
    
    if stock is None:
        raise ConcurrentModificationError("Stock was modified by another transaction")
    
    return stock
```

## Data Flow

### Request Flow (Stock Movement Creation)

```
User clicks "Receive Stock"
    ↓
[Frontend] MovementForm validates input
    ↓
[Frontend] POST /api/v1/movements/ with payload
    ↓
[API] MovementCreate schema validates
    ↓
[API] get_current_user dependency resolves user
    ↓
[API] get_db dependency provides AsyncSession
    ↓
[Service] MovementService.create_movement()
    ├── Validates product exists
    ├── Validates DC exists
    ├── Validates source exists
    ├── Validates stock sufficiency (for outbound)
    ├── Creates StockMovement record
    ├── Updates Stock.quantity
    ├── Updates DefectStock (if applicable)
    └── Creates AuditLog entry
    ↓
[Repository] All changes tracked in session
    ↓
[DB] Transaction commits atomically
    ↓
[API] Returns MovementRead schema
    ↓
[Frontend] Invalidates stock queries, shows success
```

### State Management Flow

```
[React Query Cache]
    │
    ├── useQuery(['products']) ──────────→ Products Page
    ├── useQuery(['stock', dcId]) ───────→ Stock Page  
    ├── useQuery(['movements', filters]) → Movements Page
    │
    └── useMutation(createMovement)
           │
           ├── onSuccess: queryClient.invalidateQueries(['stock'])
           │                        .invalidateQueries(['movements'])
           │
           └── onError: Show error notification
```

### Key Data Flows

1. **Stock Receiving:** Source → DC Stock (increment) → Movement record → Audit log
2. **Stock Dispatch:** DC Stock (decrement, validate first) → Movement record → Audit log
3. **Stock Transfer:** Source DC Stock (decrement) → Dest DC Stock (increment) → Movement record → Audit log
4. **Defect Registration:** Stock (decrement) → DefectStock (increment) → Movement record → Audit log
5. **Stock Adjustment:** Stock (set value) → Movement record (adjustment type) → Audit log

## Component Boundaries & Communication

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           BOUNDARY MAP                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌─────────────┐                        ┌─────────────┐                 │
│   │   Products  │ ─── validated by ───→  │   Stock     │                 │
│   │   Module    │                        │   Module    │                 │
│   └─────────────┘                        └──────┬──────┘                 │
│         │                                       │                         │
│         │                              creates/updates                    │
│         │                                       │                         │
│         │                                       ▼                         │
│         │              ┌─────────────────────────────────┐               │
│         │              │       StockMovements           │               │
│         │              │       (9 operation types)      │               │
│         │              └──────────────┬────────────────┘               │
│         │                             │                                  │
│         │                    logs to  │                                  │
│         │                             ▼                                  │
│         │              ┌─────────────────────────────────┐              │
│         └─────────────→│         AuditLog               │              │
│                        │    (immutable event stream)    │              │
│                        └─────────────────────────────────┘              │
│                                                                           │
│   ┌─────────────┐         owns            ┌─────────────┐               │
│   │   Sources   │ ────────────────────→   │ StockMovements│              │
│   │  (suppliers)│                        │   (incoming) │               │
│   └─────────────┘                        └─────────────┘               │
│                                                                           │
│   ┌─────────────┐         holds           ┌─────────────┐               │
│   │ Distribution│ ────────────────────→   │    Stock    │               │
│   │  Centers    │                        │   (per DC)  │               │
│   └─────────────┘                        └─────────────┘               │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Internal Communication Rules

| From → To | Allowed? | How | Notes |
|-----------|----------|-----|-------|
| API → Service | ✓ | Direct call | API handlers should be thin |
| API → CRUD | ✗ | - | Must go through Service |
| Service → Service | ✓ | Direct call | For cross-domain operations |
| Service → CRUD | ✓ | Direct call | Normal path |
| CRUD → CRUD | △ | Via session | Only for joins, prefer Service coordination |
| Service → Model | ✓ | Read only | Never business logic in models |

## Build Order (Phase Dependencies)

Based on component dependencies, recommended build order:

```
Phase 1: Foundation (No dependencies)
├── Database setup (PostgreSQL + async engine)
├── Core models (User, DistributionCenter, Source)
├── Authentication (JWT, password hashing)
└── Basic CRUD patterns

Phase 2: Product Management (Depends on Phase 1)
├── Product model
├── Product CRUD
├── Product API endpoints
└── Frontend Products page

Phase 3: Stock Core (Depends on Phase 2)
├── Stock model (linked to Product + DC)
├── Stock CRUD
├── Stock API (read-only initially)
├── Stock validation service
└── Frontend Stock page (display)

Phase 4: Stock Operations (Depends on Phase 3)
├── StockMovement model
├── MovementService (9 operation types)
├── Transaction handling
├── Stock update logic (with validation)
└── Frontend Movements page (create/list)

Phase 5: Defect Management (Depends on Phase 4)
├── DefectStock model
├── Defect operations (defect_register, defect_writeoff)
├── Defect API endpoints
└── Frontend Defects page

Phase 6: Audit & Reporting (Depends on Phase 4)
├── AuditLog model
├── AuditService
├── Reporting endpoints
└── Frontend Reports/History pages
```

### Dependency Graph

```
         Users
           │
           ▼
    DistributionCenters    Sources
           │                 │
           └────────┬────────┘
                    ▼
                Products
                    │
                    ▼
                  Stock
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
    StockMovements  │   DefectStock
          │         │         │
          └─────────┼─────────┘
                    ▼
                AuditLog
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Monolith FastAPI is fine. Single PostgreSQL instance. |
| 1k-10k users | Add connection pooling (PgBouncer). Add read replicas for reporting. |
| 10k-100k users | Consider caching (Redis) for product catalog. Separate read API for reports. |
| 100k+ users | Consider microservices: split Stock Service from Product Service. Event-driven sync. |

### Scaling Priorities

1. **First bottleneck:** Database connections → Use connection pooling, tune pool size
2. **Second bottleneck:** Stock queries → Add indexes on (product_id, dc_id), consider materialized views for stock summaries
3. **Third bottleneck:** Report queries → Move to read replica, consider time-series aggregation

## Anti-Patterns

### Anti-Pattern 1: Business Logic in API Handlers

**What people do:** Put stock validation directly in `@router.post()` handler.

**Why it's wrong:** 
- Can't reuse logic from other endpoints
- Testing requires HTTP client
- Logic scattered across files

**Do this instead:** Extract to Service layer. API handler just parses request and calls service.

```python
# BAD
@router.post("/movements/")
async def create_movement(movement: MovementCreate, db: AsyncSession):
    stock = await db.execute(select(Stock).where(...))
    if stock.quantity < movement.quantity:
        raise HTTPException(400, "Insufficient stock")
    # ... more logic in handler

# GOOD
@router.post("/movements/")
async def create_movement(
    movement: MovementCreate,
    service: MovementService = Depends(get_movement_service),
):
    return await service.create_movement(movement)  # Service handles all logic
```

### Anti-Pattern 2: Skipping Transactions for Stock Updates

**What people do:** Update stock, then create movement record in separate calls.

**Why it's wrong:** If movement creation fails, stock is already changed. Data inconsistency.

**Do this instead:** All stock-related operations in single transaction.

```python
# BAD
stock.quantity += delta
await db.commit()  # Stock updated
movement = StockMovement(...)
db.add(movement)
await db.commit()  # If this fails, stock is already wrong!

# GOOD
async with db.begin():
    stock.quantity += delta
    movement = StockMovement(...)
    db.add(movement)
    # Both commit together, or both roll back
```

### Anti-Pattern 3: Mutable Audit Logs

**What people do:** Allow updating or deleting audit log entries.

**Why it's wrong:** Audit trail is compromised. Can't trust history for compliance/debugging.

**Do this instead:** Audit logs are append-only. Corrections create new entries.

```python
# BAD - allowing updates
@router.put("/audit-log/{id}")
async def update_audit_log(id: int, data: AuditUpdate):
    ...

# GOOD - corrections via new entries
@router.post("/audit-log/correction")
async def create_correction(original_id: int, correction_data: dict):
    # Create new entry referencing original
    # Original remains immutable
    ...
```

### Anti-Pattern 4: N+1 Queries in Stock Lists

**What people do:** Fetch stock, then fetch product for each row.

**Why it's wrong:** 100 stock items = 101 queries. Performance disaster.

**Do this instead:** Use SQLAlchemy eager loading.

```python
# BAD
stocks = await crud.stock.get_multi(db)
for stock in stocks:
    product = await crud.product.get(db, stock.product_id)  # N+1!

# GOOD
stmt = select(Stock).options(selectinload(Stock.product))
stocks = await db.execute(stmt)
```

## Integration Points

### External Services (Future)

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Marketplace API | REST client, async | Sync product catalog, push stock levels |
| SMS/Email notifications | Background tasks | Async, retry with exponential backoff |
| File storage (S3) | Presigned URLs | For product images, import/export files |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Stock ↔ Movements | Service layer | Never bypass — stock changes only via movements |
| Products ↔ Stock | Foreign key + validation | Product deletion blocked if stock exists |
| Frontend ↔ Backend | REST API only | No direct DB access from frontend |
| Audit ↔ Everything | Event emission | Services emit events, audit logs them |

## Sources

- **FastAPI Documentation** (Context7 - /websites/fastapi_tiangolo) - Project structure, dependency injection
- **SQLAlchemy 2.1 Documentation** (Context7 - /websites/sqlalchemy_en_21) - Async session, Unit of Work
- **FastAPI Boilerplate** (Context7 - /websites/benavlabs_github_io_fastapi-boilerplate) - Layered architecture patterns
- **Ant Design Pro** (Context7 - /websites/pro_ant_design_zh-cn) - Frontend project structure
- **Martin Fowler - Patterns of Enterprise Architecture** - Domain Events, Unit of Work, Repository patterns
- **Martin Fowler - Domain Event** - Event sourcing patterns for audit trails

---
*Architecture research for: WMS/Fulfillment System*
*Researched: 2026-02-18*
