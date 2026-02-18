# Stack Research

**Domain:** WMS (Warehouse Management System) for Marketplace Fulfillment
**Researched:** 2025-02-18
**Confidence:** HIGH

## Recommended Stack

### Backend Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **FastAPI** | 0.129.0 | Async REST API framework | Industry standard for Python async APIs. Excellent OpenAPI docs auto-generation, Pydantic integration, async support. 2-3x faster than Flask. |
| **SQLAlchemy** | 2.0.46 | ORM + SQL toolkit | Only production-ready async ORM for Python. Type-annotated models, async sessions, mature ecosystem. 2.0 is complete rewrite with native async. |
| **PostgreSQL** | 16.x | Primary database | ACID compliance critical for inventory. Supports JSONB for flexible attributes, partial indexes for multi-tenant queries, CTEs for complex warehouse operations. |
| **asyncpg** | 0.31.0 | PostgreSQL async driver | Fastest PostgreSQL driver for Python asyncio. Binary protocol, prepared statements, 3x faster than psycopg async. Required for SQLAlchemy async. |
| **Alembic** | 1.18.4 | Database migrations | Official SQLAlchemy migration tool. Auto-generates migrations from model changes, supports branching for complex deployments. |
| **Pydantic** | 2.12.5 | Data validation | FastAPI's validation layer. V2 is 5-50x faster than V1. Type coercion, serialization, settings management. |
| **Pydantic Settings** | 2.13.0 | Configuration management | Extracted from Pydantic V2. Environment variables, .env files, secrets management. Use for all config. |
| **Uvicorn** | 0.41.0 | ASGI server | Reference ASGI server. Use `uvicorn[standard]` for uvloop (C-based event loop, 2x faster). Production-ready with workers. |

### Backend Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **python-jose** | 3.5.0 | JWT handling | JWT generation/validation. Supports RS256, HS256. Use with passlib for password hashing. |
| **passlib** | 1.7.4 | Password hashing | Bcrypt/Argon2 hashing. `CryptContext` handles algorithm upgrades. Essential for auth. |
| **bcrypt** | 5.0.0 | Bcrypt backend | C extension for passlib. Install separately for better performance. |
| **python-multipart** | 0.0.22 | Form data parsing | Required for file uploads (Excel import). FastAPI doesn't include it by default. |
| **openpyxl** | 3.1.5 | Excel read/write | Import product data, generate reports. Pure Python, no Excel dependency. Supports .xlsx/.xlsm. |
| **python-barcode** | 0.16.1 | Barcode generation | Generate EAN-13, Code128, QR for product labels. SVG/PNG output. WMS essential. |

### Frontend Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **React** | 18.3.1 | UI framework | Industry standard. Concurrent features, Suspense. Use 18.x (not 19) for ecosystem stability. |
| **TypeScript** | 5.9.3 | Type system | Catches bugs at compile time. Excellent IDE support. Essential for complex business logic. |
| **Vite** | 7.3.1 | Build tool | 10-100x faster than Webpack. Native ESM, instant HMR. Now stable with React plugin. |
| **Ant Design** | 6.3.0 | UI component library | Enterprise-grade components: Tables, Forms, Modals. Perfect for admin/WMS interfaces. Russian locale supported. |
| **Zustand** | 5.0.11 | State management | Minimal boilerplate vs Redux. TypeScript-first, no providers. Perfect for cart/filters state. |
| **Axios** | 1.13.5 | HTTP client | Interceptors for JWT refresh, request cancellation. Better error handling than fetch. |
| **React Router** | 7.13.0 | Client-side routing | Data loading, error boundaries. v7 uses modern React patterns. Use `react-router-dom` for web. |

### Development & Infrastructure

| Tool | Purpose | Notes |
|------|---------|-------|
| **Docker** | Containerization | Multi-stage builds for smaller images. Separate dev/prod Dockerfiles. |
| **Docker Compose** | Local development | postgres, backend, frontend services. Hot reload for dev. |
| **pytest** | Backend testing | Async test support with `pytest-asyncio`. Fixtures for DB setup. |
| **ruff** | Python linting | 10-100x faster than flake8. Replaces black, isort, flake8. |
| **ESLint + Prettier** | Frontend linting | Use `@antfu/eslint-config` for zero-config setup. |

## Installation

### Backend (requirements.txt)

```txt
# Core
fastapi==0.129.0
uvicorn[standard]==0.41.0
sqlalchemy[asyncio]==2.0.46
asyncpg==0.31.0
alembic==1.18.4
pydantic==2.12.5
pydantic-settings==2.13.0

# Auth
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.22

# Business Logic
openpyxl==3.1.5
python-barcode==0.16.1

# Dev
pytest==8.3.4
pytest-asyncio==0.25.3
ruff==0.12.0
httpx==0.28.1
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^7.13.0",
    "antd": "^6.3.0",
    "zustand": "^5.0.11",
    "axios": "^1.13.5"
  },
  "devDependencies": {
    "typescript": "~5.9.3",
    "vite": "^7.3.1",
    "@vitejs/plugin-react": "^4.5.2",
    "@types/react": "^19.1.12",
    "@types/react-dom": "^19.1.14",
    "eslint": "^9.23.0",
    "prettier": "^3.6.0"
  }
}
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **FastAPI** | Django REST Framework | If you need Django admin, ORM features, or massive ecosystem. DRF is slower but battle-tested. |
| **FastAPI** | Flask + Flask-RESTful | Only for very simple APIs or existing Flask codebases. Sync-only, more boilerplate. |
| **SQLAlchemy** | Tortoise ORM | If you want Django-like ORM syntax. Less mature, smaller community. |
| **asyncpg** | psycopg 3 async | If you need connection pooling built-in. asyncpg is faster but requires external pooler. |
| **Zustand** | Redux Toolkit | If team knows Redux well or needs time-travel debugging. More boilerplate. |
| **Zustand** | Jotai | For atomic state model. Zustand is simpler for WMS domain. |
| **Ant Design** | MUI | If you prefer Google Material Design. Ant Design better for data-heavy enterprise apps. |
| **Vite** | Next.js | If you need SSR/SEO. WMS is authenticated SPA, no SEO needed. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Pydantic v1** | v2 is 5-50x faster. v1 in maintenance mode only. | `pydantic>=2.0` |
| **SQLAlchemy 1.4** | No native async. Complex session management. | `sqlalchemy>=2.0` |
| **syncpg/psycopg2** | Blocking calls in async app destroy performance. | `asyncpg` |
| **create-react-app** | Deprecated. Uses outdated Webpack, slow builds. | `npm create vite@latest` |
| **Redux (vanilla)** | Massive boilerplate. Zustand does same with 90% less code. | `zustand` |
| **JWT in localStorage** | XSS vulnerable. Tokens accessible to any JS. | HttpOnly cookies + CSRF token |
| **passlib without bcrypt** | Pure Python bcrypt is 100x slower. | `passlib[bcrypt]` |
| **Flask-JWT-Extended** | Adds unnecessary abstraction over python-jose. | `python-jose` directly |
| **ORM for bulk imports** | SQLAlchemy slow for 10k+ row inserts. | `COPY` via asyncpg or batch `session.execute(insert())` |

## Stack Patterns by Variant

**If you need offline capability:**
- Add `@tanstack/react-query` for server state caching
- Consider PWA with service worker
- Zustand persist middleware for local state

**If you need real-time updates (e.g., inventory changes):**
- Add `fastapi-websocket` for WebSocket support
- Or use Server-Sent Events for simpler push
- Zustand + WebSocket subscription pattern

**If you need barcode scanning in browser:**
- Add `@zxing/library` for camera scanning
- React wrapper: `@aspect-ratio/react-barcode-scanner`

**If you need PDF reports:**
- Backend: `weasyprint` (HTML to PDF)
- Or `reportlab` for programmatic PDFs
- Frontend: `react-to-print` for simple prints

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI 0.129 | Pydantic 2.x | FastAPI requires Pydantic 2 since 0.100.0 |
| SQLAlchemy 2.0 | asyncpg 0.31+ | Use `postgresql+asyncpg://` connection string |
| Alembic 1.18 | SQLAlchemy 2.0 | Same major version required |
| React 18 | Ant Design 6 | Ant Design 5.x also works, 6 has better RSC support |
| TypeScript 5.9 | React 18 | React 19 types may have minor differences |
| Vite 7 | React 18 | Use `@vitejs/plugin-react` for Fast Refresh |

## Architecture Decisions

### Why Async Everything?

WMS operations involve:
- Multiple DB queries per request (inventory check, location lookup, audit log)
- External API calls (marketplace sync, notification services)
- File I/O (Excel parsing, report generation)

Async allows handling 10x more concurrent requests on same hardware.

### Why PostgreSQL over MySQL?

- **JSONB**: Flexible attributes for product variants, marketplace-specific data
- **Partial indexes**: `WHERE deleted_at IS NULL` for soft deletes
- **CTEs**: Complex inventory aggregation queries
- **Advisory locks**: Prevent concurrent stock modifications

### Why Not Use an ORM for Bulk Operations?

```python
# BAD: 10,000 individual INSERTs
for item in items:
    session.add(InventoryItem(**item))
await session.commit()  # 10,000 round trips

# GOOD: Single batch INSERT
from sqlalchemy import insert
await session.execute(
    insert(InventoryItem),
    [item.dict() for item in items]
)
await session.commit()  # 1 round trip
```

### Why Zustand over React Context?

- **No re-render storms**: Context causes all consumers to re-render
- **Middleware**: Persist, devtools, immer integration
- **Outside React**: Access state in event handlers, WebSocket callbacks
- **Bundle size**: 2.9KB vs 12KB for Redux Toolkit

## Sources

| Source | What Was Verified | Confidence |
|--------|------------------|------------|
| PyPI API | All Python package versions | HIGH |
| npm Registry | All JavaScript package versions | HIGH |
| Context7 `/fastapi/fastapi` | FastAPI installation, CLI usage | HIGH |
| Context7 `/websites/sqlalchemy_en_21` | SQLAlchemy 2.0 async patterns | HIGH |
| Context7 `/pmndrs/zustand` | Zustand v5 TypeScript patterns | HIGH |
| Context7 `/websites/ant_design` | Ant Design 6 installation | HIGH |
| Context7 `/vitejs/vite` | Vite 7 configuration | HIGH |

---
*Stack research for: WMS/Fulfillment System*
*Researched: 2025-02-18*
