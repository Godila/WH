# Requirements: WMS Marketplace

**Defined:** 2026-02-18
**Core Value:** Точные остатки на фулфилменте без ручного пересчёта и ошибок.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [ ] **AUTH-01**: Пользователь может войти с email и паролем
- [ ] **AUTH-02**: JWT токен выдаётся при успешном логине
- [ ] **AUTH-03**: API эндпоинты защищены — требуют валидный токен
- [ ] **AUTH-04**: Пользователь может получить информацию о текущем пользователе

### Products (Master Data)

- [ ] **PROD-01**: Можно создать товар с полями: barcode, gtin, seller_sku, size, brand, color
- [ ] **PROD-02**: Barcode уникален в системе
- [ ] **PROD-03**: GTIN уникален в системе
- [ ] **PROD-04**: Можно редактировать товар
- [ ] **PROD-05**: Можно удалить товар (soft delete)
- [ ] **PROD-06**: Список товаров с пагинацией
- [ ] **PROD-07**: Поиск товара по баркоду
- [ ] **PROD-08**: Список товаров с остатками (stock_quantity, defect_quantity)

### Sources (Master Data)

- [ ] **SRC-01**: Справочник источников (ПВЗ, поставщики)
- [ ] **SRC-02**: CRUD для источников
- [ ] **SRC-03**: Seed-данные: 4 источника при инициализации

### Distribution Centers (Master Data)

- [ ] **DC-01**: Справочник РЦ маркетплейсов
- [ ] **DC-02**: CRUD для РЦ
- [ ] **DC-03**: Seed-данные: 9 РЦ при инициализации

### Stock & DefectStock

- [ ] **STOCK-01**: Запись Stock создаётся автоматически при создании товара (quantity=0)
- [ ] **STOCK-02**: Запись DefectStock создаётся автоматически при создании товара (quantity=0)
- [ ] **STOCK-03**: Остатки обновляются автоматически при операциях движения
- [ ] **STOCK-04**: Валидация: нельзя отгрузить больше чем есть на Stock
- [ ] **STOCK-05**: Валидация: нельзя утилизировать больше чем есть на DefectStock

### Stock Movements (9 Operations)

- [ ] **MOVE-01**: RECEIPT — приёмка годного товара (Stock += n)
- [ ] **MOVE-02**: RECEIPT_DEFECT — приёмка брака (DefectStock += n)
- [ ] **MOVE-03**: SHIPMENT_RC — отгрузка в РЦ (Stock -= n), требует distribution_center_id
- [ ] **MOVE-04**: RETURN_PICKUP — возврат годного с ПВЗ (Stock += n), требует source_id
- [ ] **MOVE-05**: RETURN_DEFECT — возврат брака (DefectStock += n), требует source_id
- [ ] **MOVE-06**: SELF_PURCHASE — самовыкуп (Stock += n), требует source_id
- [ ] **MOVE-07**: WRITE_OFF — списание в брак (Stock -= n, DefectStock += n)
- [ ] **MOVE-08**: RESTORATION — восстановление (DefectStock -= n, Stock += n)
- [ ] **MOVE-09**: UTILIZATION — утилизация (DefectStock -= n)
- [ ] **MOVE-10**: Все операции атомарны — транзакция либо проходит целиком, либо откатывается
- [ ] **MOVE-11**: Условные поля: source_id обязателен для RETURN_*, SELF_PURCHASE
- [ ] **MOVE-12**: Условные поля: distribution_center_id обязателен для SHIPMENT_RC

### Movement Journal

- [ ] **JRN-01**: Все операции записываются в StockMovements
- [ ] **JRN-02**: Фильтрация по типу операции
- [ ] **JRN-03**: Фильтрация по товару (product_id)
- [ ] **JRN-04**: Фильтрация по дате (from, to)
- [ ] **JRN-05**: Пагинация журнала
- [ ] **JRN-06**: Сортировка по дате DESC (новые сверху)

### Excel Import

- [ ] **IMP-01**: Импорт товаров из Excel (лист "Сводная")
- [ ] **IMP-02**: Маппинг колонок: Баркод, Артикул продавца, Размер, Бренд, Артикул WB, АКТУАЛЬНЫЙ ОСТАТОК, БРАКИ
- [ ] **IMP-03**: Upsert логика: товар существует по баркоду — обновить, нет — создать
- [ ] **IMP-04**: Создание Stock и DefectStock записей при импорте
- [ ] **IMP-05**: Обработка пустых/нулевых значений (БРАКИ = 0 если пусто)

### Reports & Analytics

- [ ] **RPT-01**: GET /api/stock/summary — сводный отчёт (total_products, total_stock, total_defect)
- [ ] **RPT-02**: Dashboard со статистикой: всего товаров, общий остаток, общий брак

### Frontend

- [ ] **UI-01**: Страница логина (email, password)
- [ ] **UI-02**: Dashboard — таблица товаров с колонками: баркод, GTIN, артикул, бренд, размер, остаток, брак, итого
- [ ] **UI-03**: Dashboard — поиск по баркоду/артикулу
- [ ] **UI-04**: Dashboard — статистика сверху (всего товаров, общий остаток, общий брак)
- [ ] **UI-05**: Форма проведения операции с выбором типа
- [ ] **UI-06**: Динамические поля в форме: source_id для RETURN_*/SELF_PURCHASE, distribution_center_id для SHIPMENT_RC
- [ ] **UI-07**: Autocomplete товара по баркоду/артикулу
- [ ] **UI-08**: Журнал движений — таблица с фильтрами (тип, дата, товар)
- [ ] **UI-09**: Журнал движений — пагинация
- [ ] **UI-10**: Цветовая кодировка: зелёный (годное), оранжевый (брак), синий (отгрузки)
- [ ] **UI-11**: Обработка ошибок API — сообщения пользователю
- [ ] **UI-12**: Loading-стейты при запросах
- [ ] **UI-13**: Редирект на логин при истечении токена

### Infrastructure

- [ ] **INF-01**: Docker Compose с postgres + backend + frontend
- [ ] **INF-02**: Миграции БД через Alembic
- [ ] **INF-03**: Автоинициализация БД с seed-данными при первом запуске
- [ ] **INF-04**: Healthchecks для контейнеров
- [ ] **INF-05**: Swagger документация (/docs)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Excel Export
- **EXP-01**: Экспорт журнала движений в Excel
- **EXP-02**: Экспорт остатков в Excel

### Advanced Features
- **ADV-01**: Поиск по GTIN
- **ADV-02**: Уведомления о низких остатках
- **ADV-03**: Barcode/QR сканирование
- **ADV-04**: Интеграция с API маркетплейсов (WB, Ozon)

### Roles & Permissions
- **ROLE-01**: Роли пользователей (admin, operator)
- **ROLE-02**: Разграничение прав доступа

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Учёт остатков на маркетплейсах | Только свои склады фулфилмента |
| Мобильное приложение | Web-first, desktop-first |
| API интеграция с маркетплейсами | Вручную вводим операции |
| WebSocket real-time | Polling достаточен для MVP |
| Сложные picking алгоритмы | Overkill для 2-3 пользователей |
| Multi-tenant | Одна компания |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1 | Complete |
| AUTH-02 | Phase 1 | Complete |
| AUTH-03 | Phase 1 | Complete |
| AUTH-04 | Phase 1 | Complete |
| PROD-01 | Phase 2 | Complete |
| PROD-02 | Phase 2 | Complete |
| PROD-03 | Phase 2 | Complete |
| PROD-04 | Phase 2 | Complete |
| PROD-05 | Phase 2 | Complete |
| PROD-06 | Phase 2 | Complete |
| PROD-07 | Phase 2 | Complete |
| PROD-08 | Phase 2 | Complete |
| SRC-01 | Phase 1 | Complete |
| SRC-02 | Phase 1 | Complete |
| SRC-03 | Phase 1 | Complete |
| DC-01 | Phase 1 | Complete |
| DC-02 | Phase 1 | Complete |
| DC-03 | Phase 1 | Complete |
| STOCK-01 | Phase 2 | Complete |
| STOCK-02 | Phase 2 | Complete |
| STOCK-03 | Phase 3 | Complete |
| STOCK-04 | Phase 3 | Complete |
| STOCK-05 | Phase 3 | Complete |
| MOVE-01 | Phase 3 | Complete |
| MOVE-02 | Phase 3 | Complete |
| MOVE-03 | Phase 3 | Complete |
| MOVE-04 | Phase 3 | Complete |
| MOVE-05 | Phase 3 | Complete |
| MOVE-06 | Phase 3 | Complete |
| MOVE-07 | Phase 3 | Complete |
| MOVE-08 | Phase 3 | Complete |
| MOVE-09 | Phase 3 | Complete |
| MOVE-10 | Phase 3 | Complete |
| MOVE-11 | Phase 3 | Complete |
| MOVE-12 | Phase 3 | Complete |
| JRN-01 | Phase 3 | Complete |
| JRN-02 | Phase 3 | Complete |
| JRN-03 | Phase 3 | Complete |
| JRN-04 | Phase 3 | Complete |
| JRN-05 | Phase 3 | Complete |
| JRN-06 | Phase 3 | Complete |
| IMP-01 | Phase 4 | Complete |
| IMP-02 | Phase 4 | Complete |
| IMP-03 | Phase 4 | Complete |
| IMP-04 | Phase 4 | Complete |
| IMP-05 | Phase 4 | Complete |
| RPT-01 | Phase 3 | Complete |
| RPT-02 | Phase 5 | Complete |
| UI-01 | Phase 5 | Complete |
| UI-02 | Phase 5 | Complete |
| UI-03 | Phase 5 | Complete |
| UI-04 | Phase 5 | Complete |
| UI-05 | Phase 5 | Complete |
| UI-06 | Phase 5 | Complete |
| UI-07 | Phase 5 | Complete |
| UI-08 | Phase 5 | Complete |
| UI-09 | Phase 5 | Complete |
| UI-10 | Phase 5 | Complete |
| UI-11 | Phase 5 | Complete |
| UI-12 | Phase 5 | Complete |
| UI-13 | Phase 5 | Complete |
| INF-01 | Phase 6 | Pending |
| INF-02 | Phase 1 | Complete |
| INF-03 | Phase 1 | Complete |
| INF-04 | Phase 6 | Pending |
| INF-05 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 67 total
- Mapped to phases: 67
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-18*
*Last updated: 2026-02-19 after Phase 5 completion*
