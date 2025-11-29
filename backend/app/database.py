from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
from geoalchemy2 import Geometry

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle database URL scheme for asyncpg
db_url = settings.database_url
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Log masked URL for debugging
    masked_url = db_url.split("@")[-1] if "@" in db_url else "..."
    logger.info(f"Attempting to connect to database at: {masked_url}")
else:
    logger.error("DATABASE_URL is not set!")


engine = create_async_engine(
    db_url,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    connect_args={
        "ssl": "prefer",
        "statement_cache_size": 0
    }
    )

    #create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
    )

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
