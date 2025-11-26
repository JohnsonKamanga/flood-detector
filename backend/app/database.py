from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
from geoalchemy2 import Geometry

engine = create_async_engine(
    settings.database_url.replace("postgres://", "postgresql+asyncpg://"), 
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40
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
