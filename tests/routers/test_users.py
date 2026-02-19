"""Tests for user profile endpoints."""

from httpx import AsyncClient


async def test_get_me(client: AsyncClient):
    resp = await client.get("/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "student@test.com"
    assert data["role"] == "STUDENT"


async def test_update_display_name(client: AsyncClient):
    resp = await client.patch("/users/me", json={"display_name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "New Name"


async def test_update_hebrew_name(client: AsyncClient):
    resp = await client.patch("/users/me", json={"hebrew_name": "Avraham"})
    assert resp.status_code == 200
    assert resp.json()["hebrew_name"] == "Avraham"


async def test_partial_update_only_changes_specified_fields(client: AsyncClient):
    resp = await client.patch("/users/me", json={"hebrew_name": "Moshe"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["hebrew_name"] == "Moshe"
    assert data["display_name"] == "Test Student"
