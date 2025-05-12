import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
