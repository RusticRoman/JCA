"""Tests for resource endpoints."""

import uuid
from unittest.mock import patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import make_resource


async def test_list_resources(client: AsyncClient, db: AsyncSession):
    r1 = make_resource(title="Guide A")
    r2 = make_resource(title="Guide B")
    db.add_all([r1, r2])
    await db.commit()

    resp = await client.get("/resources")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_download_resource(client: AsyncClient, db: AsyncSession):
    resource = make_resource(gcs_path="resources/guide.pdf")
    db.add(resource)
    await db.commit()
    await db.refresh(resource)

    with patch("app.routers.resources.get_download_url") as mock_url:
        mock_url.return_value = "https://storage.example.com/signed-url"
        resp = await client.get(f"/resources/{resource.id}/download")
        assert resp.status_code == 200
        assert resp.json()["download_url"] == "https://storage.example.com/signed-url"


async def test_download_resource_not_found(client: AsyncClient):
    resp = await client.get(f"/resources/{uuid.uuid4()}/download")
    assert resp.status_code == 404
