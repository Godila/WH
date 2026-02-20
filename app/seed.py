from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.source import Source
from app.models.distribution_center import DistributionCenter
from app.core.security import get_password_hash

# Seed data for sources (suppliers and pickup points)
SOURCES = [
    {"name": "Поставщик РФ", "description": "Основной российский поставщик"},
    {"name": "ПВЗ Казань", "description": "Пункт выдачи заказов Казань"},
    {"name": "ПВЗ Москва", "description": "Пункт выдачи заказов Москва"},
    {"name": "Прямой поставщик", "description": "Прямые поставки от производителя"},
]

# Seed data for distribution centers (marketplace fulfillment centers)
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

# Admin user credentials
ADMIN_USER = {
    "email": "admin@wms.example.com",
    "password": "admin123",
}


async def seed_database(db: AsyncSession) -> None:
    """
    Seed database with initial data if tables are empty.
    
    Creates:
    - Admin user (admin@wms.local / admin123)
    - 4 sources (suppliers and pickup points)
    - 9 distribution centers (WB and Ozon)
    
    Args:
        db: Async database session
    """
    
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
