# WMS Marketplace

Система складского учёта (WMS) для фулфилмента маркетплейсов РФ. Заменяет Excel-таблицы для учёта товаров на двух складах — основной (годный товар) и брак.

## Возможности

- **9 типов складских операций** с автоматическим пересчётом остатков
- **Два склада**: Stock (годный товар) и DefectStock (брак)
- **Журнал движений** с фильтрацией и пагинацией
- **Импорт товаров из Excel** (лист "Сводная")
- **JWT авторизация**
- **Web-интерфейс** на React + Ant Design
- **Docker-развёртывание** одной командой

## Стек технологий

| Backend | Frontend | Infrastructure |
|---------|----------|----------------|
| Python 3.12 | React 18 | Docker Compose |
| FastAPI | TypeScript | PostgreSQL 16 |
| SQLAlchemy 2.0 (async) | Vite | nginx |
| Alembic | Ant Design | |
| Pydantic | Zustand | |
| JWT (python-jose) | Axios | |

## Быстрый старт

### Требования

- Docker & Docker Compose
- Git

### Запуск

```bash
# Клонировать репозиторий
git clone https://github.com/Godila/WH.git
cd WH

# Создать .env файл
cp .env.example .env

# Запустить
docker-compose up -d --build
```

Приложение будет доступно на http://localhost

### Данные по умолчанию

При первом запуске автоматически создаются:
- **Admin пользователь:** `admin@example.com` / `admin123`
- **4 источника (ПВЗ)**
- **9 распределительных центров (РЦ)**

## 9 складских операций

| Операция | Эффект | Обязательные поля |
|----------|--------|-------------------|
| RECEIPT | Stock += n | product_id, quantity |
| RECEIPT_DEFECT | DefectStock += n | product_id, quantity |
| SHIPMENT_RC | Stock -= n | product_id, quantity, distribution_center_id |
| RETURN_PICKUP | Stock += n | product_id, quantity, source_id |
| RETURN_DEFECT | DefectStock += n | product_id, quantity, source_id |
| SELF_PURCHASE | Stock += n | product_id, quantity, source_id |
| WRITE_OFF | Stock -= n, DefectStock += n | product_id, quantity |
| RESTORATION | DefectStock -= n, Stock += n | product_id, quantity |
| UTILIZATION | DefectStock -= n | product_id, quantity |

## API документация

После запуска доступна Swagger документация:
- **Swagger UI:** http://localhost/api/docs
- **ReDoc:** http://localhost/api/redoc

### Основные эндпоинты

```
POST   /api/auth/login              # Авторизация
GET    /api/auth/me                 # Текущий пользователь

GET    /api/products/               # Список товаров (с остатками)
POST   /api/products/               # Создать товар
PUT    /api/products/{id}           # Обновить товар
DELETE /api/products/{id}           # Удалить товар (soft delete)

POST   /api/stock/movements         # Провести операцию
GET    /api/stock/movements         # Журнал движений
GET    /api/stock/summary           # Статистика

POST   /api/import/excel            # Импорт из Excel

GET    /api/sources/                # Источники (ПВЗ)
GET    /api/distribution-centers/   # Распределительные центры
```

## Структура проекта

```
WH/
├── app/                    # Backend (FastAPI)
│   ├── api/                # API endpoints
│   │   ├── auth.py         # Авторизация
│   │   ├── products.py     # Товары
│   │   ├── stock.py        # Складские операции
│   │   └── import_excel.py # Импорт Excel
│   ├── core/               # Конфигурация
│   ├── models/             # SQLAlchemy модели
│   ├── schemas/            # Pydantic схемы
│   ├── services/           # Бизнес-логика
│   └── main.py             # FastAPI app
├── frontend/               # Frontend (React)
│   └── src/
│       ├── api/            # API клиент
│       ├── components/     # React компоненты
│       ├── pages/          # Страницы
│       ├── types/          # TypeScript типы
│       └── utils/          # Утилиты
├── alembic/                # Миграции БД
├── docker-compose.yml      # Docker Compose
├── Dockerfile.backend      # Backend Dockerfile
├── Dockerfile.frontend     # Frontend Dockerfile
└── nginx.conf              # nginx конфигурация
```

## Импорт из Excel

Excel файл должен содержать лист "Сводная" с колонками:

| Колонка | Описание |
|---------|----------|
| Баркод | Штрихкод товара (обязательно) |
| Артикул продавца | Seller SKU |
| Размер | Размер |
| Бренд | Бренд |
| Артикул WB | Артикул Wildberries (сохраняется в GTIN) |
| АКТУАЛЬНЫЙ ОСТАТОК | Количество годного товара |
| БРАКИ | Количество брака |

Логика: товар существует по баркоду → обновить, иначе → создать.

## Разработка

### Backend

```bash
cd WH
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Миграции
alembic upgrade head

# Запуск
fastapi dev app/main.py
```

### Frontend

```bash
cd WH/frontend
npm install
npm run dev
```

## Безопасность

- JWT токены с настраиваемым сроком действия
- Пароли хешируются bcrypt
- Soft delete для товаров (данные не теряются)
- Валидация на всех уровнях (Pydantic, SQLAlchemy)

## Лицензия

MIT
