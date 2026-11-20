"""Health endpoints: the legacy unprefixed path and the versioned alias."""

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("path", ["/healthz", "/api/v1/healthz"])
async def test_healthz_returns_ok(client: AsyncClient, path: str) -> None:
    response = await client.get(path)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
