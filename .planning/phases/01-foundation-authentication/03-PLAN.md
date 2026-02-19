---
phase: 01-foundation-authentication
plan: 03
type: execute
wave: 2
depends_on: [01]
files_modified:
  - app/seed.py
  - app/main.py
autonomous: true

must_haves:
  truths:
    - "4 source records exist in database after initialization"
    - "9 distribution center records exist after database initialization"
    - "Admin user exists for testing login"
  artifacts:
    - path: "app/seed.py"
      provides: "Initial data seeding"
      exports: ["seed_database"]
    - path: "app/main.py"
      provides: "FastAPI application"
      contains: "lifespan"
  key_links:
    - from: "app/main.py"
      to: "app/seed.py"
      via: "lifespan startup event"
      pattern: "seed_database"
    - from: "app/seed.py"
      to: "app/database.py"
      via: "async_session"
      pattern: "async_session"
---

<objective>
Create seed data script to populate reference data and admin user on first startup.

Purpose: Ensure the system has the required initial data (4 sources, 9 distribution centers, admin user) without manual database operations.

Output: Automatic data initialization when app starts with empty tables.
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
  <name>Task 1: Create seed script</name>
  <files>
    app/seed.py
  </files>
  <action>
Create seed.py with initial data for sources, distribution centers, and admin user:

**app/seed.py:**
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.source import Source
from app.models.distribution_center import DistributionCenter
from app.core.security import get_password_hash

SOURCES = [
    {"name": "Поставщик РФ", "description": "Основной российский поставщик"},
    {"name": "ПВЗ Казань", "description": "Пункт выдачи заказов Казань"},
    {"name": "ПВЗ Москва", "description": "Пункт выдачи заказов Москва"},
    {"name": "Прямой поставщик", "description": "Прямые поставки от производителя"},
]

DISTRIBUTION_CENTERS = [
    {"code": "WB-KAZAN", "name": "Казань WB", "marketplace": "WB"},
    {"code": "WB-MOSCOW", "name": "Москва WB", "marketplace": "WB"},
    {"code": "WB-STPETERSBURG", "name": "Санкт-Петербург WB", "marketplace": "WB"},
    {"code": "WB-KRASNODAR", "name": "Краснодар WB", "marketplace": "WB"},
    {"code": "OZON-KAZAN", "name": "Казань Ozon", "marketplace": "Ozon"},
    {"code": "OZON-MOSCOW", "name": "Москва Ozon", "marketplace": "Ozon"},
    {"code": "OZON-STPETERSBURG", "name": "Санкт-Петербург Ozon", "marketplace": "Ozon"},
    {"code": "OZON-KRASNODAR", "name": "Краснодар Ozon", "marketplace": "Ozon"},
    {"code": "OZON-NOVOSIBIRSK", "name": "Новосибирск Ozon", "marketplace": "Ozon"},
]

ADMIN_USER = {
    "email": "admin@wms.local",
    "password": "admin123",  # Will be hashed
}

async def seed_database(db: AsyncSession) -> None:
    """Seed database with initial data if tables are empty."""
    
    # Seed admin user
    result = await db.execute(select(User).limit(1))
    if not result.scalar_one_or_none():
        admin = User(
            email=ADMIN_USER["email"],
            hashed_password=get_password_hash(ADMIN_USER["password"]),
            is_active=True,
        )
        db.add(admin)
        print("Created admin user: admin@wms.local / admin123")
    
    # Seed sources
    result = await db.execute(select(Source).limit(1))
    if not result.scalar_one_or_none():
        for source_data in SOURCES:
            source = Source(**source_data)
            db.add(source)
        print(f"Created {len(SOURCES)} sources")
    
    # Seed distribution centers
    result = await db.execute(select(DistributionCenter).limit(1))
    if not result.scalar_one_or_none():
        for dc_data in DISTRIBUTION_CENTERS:
            dc = DistributionCenter(**dc_data)
            db.add(dc)
        print(f"Created {len(DISTRIBUTION_CENTERS)} distribution centers")
    
    await db.commit()
```

Do NOT run migrations here - just create the seed function.
  </action>
  <verify>
python -c "from app.seed import seed_database, SOURCES, DISTRIBUTION_CENTERS; print(f'Sources: {len(SOURCES)}, DCs: {len(DISTRIBUTION_CENTERS)}')"
  </verify>
  <done>
Seed function exists with 4 sources, 9 DCs, and admin user. Function checks for existing data before inserting.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create FastAPI app with startup seed</name>
  <files>
    app/main.py
  </files>
  <action>
Create FastAPI application with lifespan event for database initialization:

**app/main.py:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import async_session
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: run migrations and seed data
    async with async_session() as db:
        await seed_database(db)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="WMS Marketplace",
    description="Warehouse Management System for Marketplace Fulfillment",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Important notes:**
- Use lifespan context manager (not on_event deprecated)
- Seed runs on every startup but checks for existing data
- Health endpoint for basic monitoring
- Swagger docs will be at /docs automatically

Do NOT add routers here - that's in plan 04.
  </action>
  <verify>
python -c "from app.main import app; print(f'App title: {app.title}')"
  </verify>
  <done>
FastAPI app created with lifespan startup. Seed runs automatically. Health endpoint exists. Swagger docs configured.
  </done>
</task>

</tasks>

<verification>
1. Seed module: `python -c "from app.seed import seed_database, SOURCES, DISTRIBUTION_CENTERS; print(len(SOURCES), len(DISTRIBUTION_CENTERS))"`
2. Main app: `python -c "from app.main import app; print(app.title)"`
3. Source count = 4, DC count = 9
</verification>

<success_criteria>
- Seed data includes 4 sources (Поставщик РФ, ПВЗ Казань, ПВЗ Москва, Прямой поставщик)
- Seed data includes 9 distribution centers (4 WB + 5 Ozon)
- Admin user created (admin@wms.local / admin123)
- Seed checks for existing data before inserting
- FastAPI app runs lifespan on startup
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation-authentication/03-SUMMARY.md`
</output>
