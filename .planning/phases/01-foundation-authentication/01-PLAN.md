---
phase: 01-foundation-authentication
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app/__init__.py
  - app/models/__init__.py
  - app/models/base.py
  - app/models/user.py
  - app/models/source.py
  - app/models/distribution_center.py
  - app/database.py
  - app/core/__init__.py
  - app/core/config.py
  - alembic.ini
  - alembic/env.py
  - alembic/versions/001_initial.py
autonomous: true

must_haves:
  truths:
    - "Database tables exist for users, sources, distribution_centers"
    - "Alembic can run migrations"
    - "Async database engine is configured"
  artifacts:
    - path: "app/models/user.py"
      provides: "User SQLAlchemy model"
      contains: "class User"
    - path: "app/models/source.py"
      provides: "Source SQLAlchemy model"
      contains: "class Source"
    - path: "app/models/distribution_center.py"
      provides: "DistributionCenter SQLAlchemy model"
      contains: "class DistributionCenter"
    - path: "app/database.py"
      provides: "Async engine and session factory"
      exports: ["engine", "async_session", "get_db"]
    - path: "alembic/versions/001_initial.py"
      provides: "Initial migration"
      contains: "upgrade"
  key_links:
    - from: "app/database.py"
      to: "app/core/config.py"
      via: "settings.DATABASE_URL"
      pattern: "settings\\.DATABASE_URL"
---

<objective>
Create database foundation with SQLAlchemy models, async engine, and Alembic migrations.

Purpose: Establish the data layer that all other components will build upon. Models define the schema, database.py provides async access, Alembic handles migrations.

Output: Working async database setup with User, Source, and DistributionCenter models ready for use.
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
  <name>Task 1: Create SQLAlchemy models</name>
  <files>
    app/__init__.py
    app/models/__init__.py
    app/models/base.py
    app/models/user.py
    app/models/source.py
    app/models/distribution_center.py
    app/core/__init__.py
    app/core/config.py
  </files>
  <action>
Create SQLAlchemy 2.0 async models following these specifications:

**Project structure:**
```
app/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── user.py
│   ├── source.py
│   └── distribution_center.py
└── core/
    ├── __init__.py
    └── config.py
```

**app/core/config.py:**
- Use pydantic-settings BaseSettings
- Settings class with: DATABASE_URL (default: postgresql+asyncpg://postgres:postgres@localhost:5432/wms), SECRET_KEY (for JWT), ACCESS_TOKEN_EXPIRE_MINUTES (default: 30)
- Environment variable support

**app/models/base.py:**
- Create async base with DeclarativeBase
- Include id (UUID), created_at, updated_at columns as mixin

**app/models/user.py:**
- User model with: id (UUID), email (unique, indexed), hashed_password, is_active (default True), created_at, updated_at

**app/models/source.py:**
- Source model for "источники" (ПВЗ, поставщики)
- Fields: id (UUID), name (unique), description (optional), created_at, updated_at

**app/models/distribution_center.py:**
- DistributionCenter model for "РЦ маркетплейсов"
- Fields: id (UUID), code (unique, e.g., "WB-KAZAN"), name (e.g., "Казань WB"), marketplace (e.g., "WB", "Ozon"), created_at, updated_at

**app/models/__init__.py:**
- Export all models

Use SQLAlchemy 2.0 style with Mapped[] type hints and mapped_column().
  </action>
  <verify>
python -c "from app.models import User, Source, DistributionCenter; print('Models imported successfully')"
  </verify>
  <done>
All three models exist with correct fields. Models can be imported without errors.
  </done>
</task>

<task type="auto">
  <name>Task 2: Setup async database engine</name>
  <files>
    app/database.py
  </files>
  <action>
Create async database configuration in app/database.py:

**Requirements:**
- Import create_async_engine, async_sessionmaker from sqlalchemy.ext.asyncio
- Create async engine using settings.DATABASE_URL
- Create async_sessionmaker with expire_on_commit=False
- Create get_db() async generator dependency for FastAPI

**Pattern:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

Do NOT create tables manually - Alembic handles migrations.
  </action>
  <verify>
python -c "from app.database import engine, async_session, get_db; print('Database module loaded')"
  </verify>
  <done>
Async engine and session factory exist. get_db dependency ready for FastAPI.
  </done>
</task>

<task type="auto">
  <name>Task 3: Initialize Alembic and create initial migration</name>
  <files>
    alembic.ini
    alembic/env.py
    alembic/script.py.mako
    alembic/versions/001_initial.py
  </files>
  <action>
Initialize Alembic for async SQLAlchemy migrations:

**Setup:**
1. Run `alembic init alembic` (if not already done)
2. Configure alembic.ini with sqlalchemy.url pointing to async postgres
3. Modify alembic/env.py for async support:
   - Import async engine from app.database
   - Import Base from app.models.base
   - Set target_metadata = Base.metadata
   - Configure async connection using run_migrations_online

**Create initial migration:**
Run `alembic revision --autogenerate -m "initial"` to create migration that includes User, Source, DistributionCenter tables.

**Key env.py changes for async:**
```python
from app.database import engine
from app.models.base import Base

target_metadata = Base.metadata

async def run_migrations_online():
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
```

Do NOT run `alembic upgrade head` yet - database may not exist.
  </action>
  <verify>
alembic current 2>&1 | head -5
ls -la alembic/versions/
  </verify>
  <done>
Alembic initialized with async support. Initial migration file exists with User, Source, DistributionCenter tables.
  </done>
</task>

</tasks>

<verification>
1. Models importable: `python -c "from app.models import User, Source, DistributionCenter"`
2. Database module works: `python -c "from app.database import engine, async_session"`
3. Alembic config valid: `alembic current` runs without error
4. Migration file exists: `ls alembic/versions/`
</verification>

<success_criteria>
- User, Source, DistributionCenter models defined with correct fields
- Async engine and session factory configured
- Alembic initialized with async support
- Initial migration ready to create tables
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation-authentication/01-SUMMARY.md`
</output>
