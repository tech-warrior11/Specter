from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Determine database URL - supports PostgreSQL and SQLite (fallback for testing)
db_url = settings.DATABASE_URL
if "sqlite" in db_url:
    engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
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
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create tables if not already present."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")
