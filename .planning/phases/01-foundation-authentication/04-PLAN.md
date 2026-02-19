---
phase: 01-foundation-authentication
plan: 04
type: execute
wave: 3
depends_on: [02, 03]
files_modified:
  - app/schemas/source.py
  - app/schemas/distribution_center.py
  - app/api/sources.py
  - app/api/distribution_centers.py
  - app/main.py
autonomous: true

must_haves:
  truths:
    - "User can CRUD sources with authenticated requests"
    - "User can CRUD distribution centers with authenticated requests"
    - "Swagger documentation accessible at /docs"
    - "Protected endpoints return 401 without valid token"
  artifacts:
    - path: "app/schemas/source.py"
      provides: "Source Pydantic schemas"
      exports: ["SourceCreate", "SourceResponse", "SourceUpdate"]
    - path: "app/schemas/distribution_center.py"
      provides: "DC Pydantic schemas"
      exports: ["DCCreate", "DCResponse", "DCUpdate"]
    - path: "app/api/sources.py"
      provides: "Sources CRUD endpoints"
      contains: "router"
    - path: "app/api/distribution_centers.py"
      provides: "DC CRUD endpoints"
      contains: "router"
    - path: "app/main.py"
      provides: "Router registration"
      pattern: "include_router"
  key_links:
    - from: "app/api/sources.py"
      to: "app/api/deps.py"
      via: "Depends(get_current_user)"
      pattern: "get_current_user"
    - from: "app/main.py"
      to: "app/api/*"
      via: "include_router"
      pattern: "include_router"
---

<objective>
Create protected CRUD endpoints for reference data and finalize FastAPI app with Swagger docs.

Purpose: Enable managers to manage sources and distribution centers through authenticated API endpoints. Verify the complete auth flow works end-to-end.

Output: Working API with protected CRUD for Sources and Distribution Centers, accessible Swagger docs at /docs.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/research/SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Sources CRUD endpoints</name>
  <files>
    app/schemas/source.py
    app/api/sources.py
  </files>
  <action>
Create Source schemas and protected CRUD endpoints:

**app/schemas/source.py:**
```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SourceResponse(SourceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**app/api/sources.py:**
Create protected CRUD endpoints:
```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.source import Source
from app.models.user import User
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=list[SourceResponse])
async def list_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Source))
    return result.scalars().all()


@router.post("/", response_model=SourceResponse, status_code=201)
async def create_source(
    data: SourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source = Source(**data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: UUID,
    data: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(source, key, value)
    
    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    await db.delete(source)
    await db.commit()
```

All endpoints MUST use `Depends(get_current_user)` for protection.
  </action>
  <verify>
python -c "from app.api.sources import router; print(f'Sources routes: {len(router.routes)}')"
  </verify>
  <done>
Sources CRUD endpoints exist with 5 routes (list, create, get, update, delete). All protected with get_current_user.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create Distribution Centers CRUD endpoints</name>
  <files>
    app/schemas/distribution_center.py
    app/api/distribution_centers.py
  </files>
  <action>
Create Distribution Center schemas and protected CRUD endpoints:

**app/schemas/distribution_center.py:**
```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class DCBase(BaseModel):
    code: str
    name: str
    marketplace: str


class DCCreate(DCBase):
    pass


class DCUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    marketplace: Optional[str] = None


class DCResponse(DCBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**app/api/distribution_centers.py:**
Create protected CRUD endpoints (same pattern as sources):
- GET /distribution-centers/ - list all
- POST /distribution-centers/ - create
- GET /distribution-centers/{dc_id} - get by ID
- PUT /distribution-centers/{dc_id} - update
- DELETE /distribution-centers/{dc_id} - delete

All endpoints MUST use `Depends(get_current_user)`.

Follow the exact same pattern as app/api/sources.py but for DistributionCenter model.
  </action>
  <verify>
python -c "from app.api.distribution_centers import router; print(f'DC routes: {len(router.routes)}')"
  </verify>
  <done>
Distribution Centers CRUD endpoints exist with 5 routes. All protected with get_current_user.
  </done>
</task>

<task type="auto">
  <name>Task 3: Register routers and verify Swagger</name>
  <files>
    app/main.py
  </files>
  <action>
Update app/main.py to include all API routers:

**Add router imports and registration:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import async_session
from app.seed import seed_database
from app.api import auth, sources, distribution_centers  # Add this


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as db:
        await seed_database(db)
    yield


app = FastAPI(
    title="WMS Marketplace",
    description="Warehouse Management System for Marketplace Fulfillment",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(distribution_centers.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Verification:**
After updating, verify:
1. App starts without errors
2. Swagger UI accessible at /docs
3. All endpoints visible in Swagger with padlock icons (requires auth)
  </action>
  <verify>
cd /root/WH && python -c "
from app.main import app
routes = [r.path for r in app.routes]
print('Routes:', len(routes))
print('Has /api/auth/login:', '/api/auth/login' in routes)
print('Has /api/sources:', any('/api/sources' in r for r in routes))
print('Has /api/distribution-centers:', any('/api/distribution-centers' in r for r in routes))
"
  </verify>
  <done>
All routers registered. Swagger docs at /docs show all endpoints with auth indicators. Health endpoint works.
  </done>
</task>

</tasks>

<verification>
1. Sources routes: `python -c "from app.api.sources import router; print(len(router.routes))"`
2. DC routes: `python -c "from app.api.distribution_centers import router; print(len(router.routes))"`
3. App routes: `python -c "from app.main import app; print([r.path for r in app.routes])"`
4. Swagger path exists: Check /docs in app routes
</verification>

<success_criteria>
- Sources CRUD: 5 protected endpoints (list, create, get, update, delete)
- Distribution Centers CRUD: 5 protected endpoints
- All endpoints require authentication (use get_current_user)
- Swagger documentation accessible at /docs
- All endpoints visible in Swagger with auth indicators
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation-authentication/04-SUMMARY.md`
</output>
