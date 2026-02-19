"""Tests for FAQ endpoints."""

import uuid

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import _override_deps
from tests.factories import make_faq


async def test_list_published_faqs(client: AsyncClient, db: AsyncSession):
    faq1 = make_faq(question="Q1?", answer="A1", order=1)
    faq2 = make_faq(question="Q2?", answer="A2", order=2, is_published=False)
    db.add_all([faq1, faq2])
    await db.commit()

    resp = await client.get("/faq")
    assert resp.status_code == 200
    data = resp.json()
    questions = [f["question"] for f in data]
    assert "Q1?" in questions
    assert "Q2?" not in questions  # unpublished


async def test_create_faq_admin(db: AsyncSession, admin_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/faq", json={
            "question": "New FAQ?",
            "answer": "New answer.",
            "order": 5,
        })
        assert resp.status_code == 201
        assert resp.json()["question"] == "New FAQ?"
    app.dependency_overrides.clear()


async def test_create_faq_student_forbidden(db: AsyncSession, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/faq", json={
            "question": "Q?", "answer": "A",
        })
        assert resp.status_code == 403
    app.dependency_overrides.clear()


async def test_update_faq(db: AsyncSession, admin_user: User):
    from app.main import create_app

    faq = make_faq()
    db.add(faq)
    await db.commit()
    await db.refresh(faq)

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.patch(f"/faq/{faq.id}", json={
            "answer": "Updated answer",
            "is_published": False,
        })
        assert resp.status_code == 200
        assert resp.json()["answer"] == "Updated answer"
    app.dependency_overrides.clear()


async def test_update_faq_not_found(db: AsyncSession, admin_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.patch(f"/faq/{uuid.uuid4()}", json={"answer": "x"})
        assert resp.status_code == 404
    app.dependency_overrides.clear()
