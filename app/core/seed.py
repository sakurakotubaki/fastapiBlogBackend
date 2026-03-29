import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.features.tags.model import Tag
from app.features.users.model import User

logger = logging.getLogger(__name__)


async def seed_superuser(db: AsyncSession) -> None:
    try:
        result = await db.execute(select(User).where(User.email == settings.SUPERUSER_EMAIL))
        if result.scalar_one_or_none():
            logger.info("Superuser already exists, skipping")
            return
        user = User(
            email=settings.SUPERUSER_EMAIL,
            hashed_password=hash_password(settings.SUPERUSER_PASSWORD),
            is_superuser=True,
        )
        db.add(user)
        await db.commit()
        logger.info("Superuser created: %s", settings.SUPERUSER_EMAIL)
    except Exception:
        logger.exception("Failed to seed superuser")


async def seed_tags(db: AsyncSession) -> None:
    try:
        for name in ["公開", "下書き"]:
            result = await db.execute(select(Tag).where(Tag.name == name))
            if not result.scalar_one_or_none():
                db.add(Tag(name=name))
        await db.commit()
        logger.info("Default tags seeded")
    except Exception:
        logger.exception("Failed to seed tags")
