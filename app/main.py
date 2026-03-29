import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

from app.core.database import async_session
from app.core.seed import seed_superuser, seed_tags
from app.features.auth.router import router as auth_router
from app.features.blogs.router import router as blogs_router
from app.features.tags.router import router as tags_router
from app.features.users.router import router as users_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with async_session() as db:
            await seed_superuser(db)
            await seed_tags(db)
    except Exception:
        logger.exception("Seed failed during startup, continuing without seed data")
    yield


app = FastAPI(title="Blog API", version="1.0.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(blogs_router)
app.include_router(tags_router)


@app.get("/")
async def root():
    return {"message": "Blog API is running"}
