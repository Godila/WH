# Roadmap: WMS Marketplace

**Milestone:** v1.0 MVP
**Created:** 2026-02-19
**Depth:** standard
**Core Value:** Точные остатки на фулфилменте без ручного пересчёта и ошибок.

## Overview

WMS система для фулфилмента маркетплейсов РФ. Заменяет Excel-таблицы для учёта товаров на двух складах (Stock + DefectStock) с автоматическим пересчётом остатков и журналом всех движений.

**Users:** 2-3 менеджера фулфилмента
**Replaces:** Excel с ручным пересчётом

---

## Phase 1: Foundation & Authentication

**Goal:** Менеджеры могут авторизоваться в системе с защищённым доступом к API

**Status:** ✓ Complete (2026-02-19)

**Dependencies:** None (foundation)

**Requirements:**
- AUTH-01, AUTH-02, AUTH-03, AUTH-04 — JWT аутентификация
- SRC-01, SRC-02, SRC-03 — Справочник источников
- DC-01, DC-02, DC-03 — Справочник РЦ
- INF-02, INF-03, INF-05 — Миграции, seed, Swagger

**Plans:** 4 plans in 4 waves

Plans:
- [x] 01-PLAN.md — Database models, async engine, Alembic migrations
- [x] 02-PLAN.md — JWT auth system (login, me, get_current_user)
- [x] 03-PLAN.md — Seed data (4 sources, 9 DCs, admin user)
- [x] 04-PLAN.md — Reference data CRUD APIs with Swagger

**Success Criteria:**
1. Менеджер может войти в систему с email и паролем
2. Система выдаёт JWT токен после успешного логина
3. Защищённые API эндпоинты отклоняют запросы без валидного токена
4. Справочники источников (4 записи) и РЦ (9 записей) инициализированы при первом запуске
5. Swagger документация доступна по адресу /docs

---

## Phase 2: Master Data & Warehouses

**Goal:** Менеджеры могут управлять товарами и видеть текущие остатки

**Status:** ✓ Complete (2026-02-19)

**Dependencies:** Phase 1 (auth, database, seed data)

**Requirements:**
- PROD-01 through PROD-08 — Управление товарами
- STOCK-01, STOCK-02 — Автосоздание Stock/DefectStock

**Plans:** 2 plans in 2 waves

Plans:
- [x] 02-01-PLAN.md — Data layer: Product/Stock/DefectStock models, schemas, migration
- [x] 02-02-PLAN.md — API layer: Products CRUD with auto-stock creation, pagination, search

**Success Criteria:**
1. Менеджер может создать товар с полями barcode, GTIN, seller_sku, size, brand, color
2. Система запрещает создание товаров с дублирующимися barcode или GTIN
3. Менеджер может найти товар по баркоду
4. При создании товара автоматически создаются записи Stock и DefectStock с quantity=0
5. Список товаров отображается с пагинацией

---

## Phase 3: Stock Core & Operations

**Goal:** Менеджеры могут проводить все 9 типов складских операций с автоматическим пересчётом остатков

**Status:** ✓ Complete (2026-02-19)

**Dependencies:** Phase 2 (products, stock records exist)

**Requirements:**
- STOCK-03, STOCK-04, STOCK-05 — Автообновление остатков, валидация
- MOVE-01 through MOVE-12 — 9 типов операций, атомарность, условные поля
- JRN-01 through JRN-06 — Журнал движений
- RPT-01 — Сводный отчёт

**Plans:** 3 plans in 3 waves

Plans:
- [x] 03-01-PLAN.md — Data layer: StockMovement model, OperationType enum, schemas, migration
- [x] 03-02-PLAN.md — Service layer: MovementService with 9 operations, validation, atomicity
- [x] 03-03-PLAN.md — API layer: Movements CRUD, journal filtering, summary endpoint

**Success Criteria:**
1. Менеджер может провести приёмку годного товара (RECEIPT) — Stock.quantity увеличивается
2. Менеджер может провести отгрузку в РЦ (SHIPMENT_RC) — Stock.quantity уменьшается, система блокирует отгрузку больше чем есть
3. Менеджер может перевести товар в брак (WRITE_OFF) — Stock уменьшается, DefectStock увеличивается атомарно
4. Менеджер может утилизировать брак (UTILIZATION) — система блокирует утилизацию больше чем есть в DefectStock
5. Журнал движений показывает историю всех операций с фильтрацией по типу, товару, дате

---

## Phase 4: Excel Import

**Goal:** Менеджеры могут импортировать товары из Excel с автоматическим созданием/обновлением

**Dependencies:** Phase 2 (products, stock records)

**Requirements:**
- IMP-01, IMP-02, IMP-03, IMP-04, IMP-05 — Импорт из Excel

**Plans:** 3 plans in 3 waves

Plans:
- [ ] 04-01-PLAN.md — Schemas + openpyxl dependency
- [ ] 04-02-PLAN.md — ExcelImportService with parsing, validation, batch upsert
- [ ] 04-03-PLAN.md — API endpoint + router wiring + verification

**Success Criteria:**
1. Менеджер может загрузить Excel файл с листом "Сводная"
2. Система создаёт новые товары или обновляет существующие по баркоду (upsert)
3. Остатки Stock и DefectStock создаются/обновляются при импорте
4. Пустые значения в колонке "БРАКИ" обрабатываются как 0

---

## Phase 5: Frontend & Reports

**Goal:** Менеджеры используют web-интерфейс для ежедневной работы с системой

**Dependencies:** Phase 3 (backend API, operations)

**Requirements:**
- RPT-02 — Dashboard статистика
- UI-01 through UI-13 — Web-интерфейс

**Success Criteria:**
1. Менеджер видит Dashboard с таблицей товаров (баркод, GTIN, артикул, бренд, размер, остаток, брак)
2. Менеджер может искать товар по баркоду или артикулу через autocomplete
3. Менеджер может провести операцию через форму с динамическими полями (source_id, distribution_center_id)
4. Менеджер видит журнал движений с цветовой кодировкой (зелёный/оранжевый/синий) и фильтрами
5. При истечении JWT токена менеджер автоматически перенаправляется на страницу логина

---

## Phase 6: Infrastructure & Deployment

**Goal:** Система развёрнута в Docker и готова к продакшен-использованию

**Dependencies:** Phase 5 (complete system)

**Requirements:**
- INF-01 — Docker Compose
- INF-04 — Healthchecks

**Success Criteria:**
1. `docker-compose up` поднимает все сервисы (postgres, backend, frontend)
2. Контейнеры имеют healthchecks и автоматически перезапускаются при падении

---

## Progress

| Phase | Status | Requirements | Progress |
|-------|--------|--------------|----------|
| 1 - Foundation & Authentication | ✓ Complete | 13 | ██████ 100% |
| 2 - Master Data & Warehouses | ✓ Complete | 10 | ██████ 100% |
| 3 - Stock Core & Operations | ✓ Complete | 22 | ██████ 100% |
| 4 - Excel Import | Not Started | 5 | ░░░░░ 0% |
| 5 - Frontend & Reports | Not Started | 14 | ░░░░░ 0% |
| 6 - Infrastructure & Deployment | Not Started | 2 | ░░░░░ 0% |

**Total:** 66 requirements across 6 phases
**Completed:** 45/66 (68%)

---

## Coverage Validation

| Category | Count | Phase Mapping |
|----------|-------|---------------|
| AUTH | 4 | Phase 1 |
| PROD | 8 | Phase 2 |
| SRC | 3 | Phase 1 |
| DC | 3 | Phase 1 |
| STOCK | 5 | Phase 2 (2), Phase 3 (3) |
| MOVE | 12 | Phase 3 |
| JRN | 6 | Phase 3 |
| IMP | 5 | Phase 4 |
| RPT | 2 | Phase 3 (1), Phase 5 (1) |
| UI | 13 | Phase 5 |
| INF | 5 | Phase 1 (3), Phase 6 (2) |

**Result:** ✓ 100% coverage, 0 orphaned requirements

---

*Roadmap created: 2026-02-19*
*Ready for phase planning: `/gsd-plan-phase 1`*
