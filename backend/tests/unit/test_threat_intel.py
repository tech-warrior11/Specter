import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models import Base
from app.services.threat_intel import threat_intel


@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with sm() as session:
        await threat_intel.seed_default_iocs(session)
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_ioc_lookup_hit_and_miss(test_session: AsyncSession):
    # Lookup known malicious lab IP and benign IP
    matches = await threat_intel.lookup(test_session, ["198.51.100.25", "10.0.0.1"])

    hit = next((m for m in matches if m.value == "198.51.100.25"), None)
    miss = next((m for m in matches if m.value == "10.0.0.1"), None)

    assert hit is not None
    assert hit.matched is True
    assert hit.classification == "malicious"
    assert hit.confidence >= 0.9

    assert miss is not None
    assert miss.matched is False
