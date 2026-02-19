"""Tests for quiz/assessment endpoints."""

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.factories import make_program, make_question, make_quiz, make_semester, make_subject, make_video


async def _create_quiz_with_questions(db: AsyncSession):
    program = make_program()
    db.add(program)
    await db.flush()
    semester = make_semester(program.id)
    db.add(semester)
    await db.flush()
    subject = make_subject(semester.id)
    db.add(subject)
    await db.flush()
    video = make_video(subject.id)
    db.add(video)
    await db.flush()
    quiz = make_quiz(video.id, passing_score=50)
    db.add(quiz)
    await db.flush()

    q1 = make_question(quiz.id, text="Q1", correct_option="A", order=1)
    q2 = make_question(quiz.id, text="Q2", correct_option="B", order=2)
    db.add_all([q1, q2])
    await db.commit()
    await db.refresh(quiz)
    await db.refresh(q1)
    await db.refresh(q2)
    return quiz, [q1, q2]


async def test_get_quiz(client: AsyncClient, db: AsyncSession):
    quiz, questions = await _create_quiz_with_questions(db)
    resp = await client.get(f"/quizzes/{quiz.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Quiz"
    assert len(data["questions"]) == 2


async def test_get_quiz_not_found(client: AsyncClient):
    resp = await client.get(f"/quizzes/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_submit_quiz_all_correct(client: AsyncClient, db: AsyncSession):
    quiz, questions = await _create_quiz_with_questions(db)
    resp = await client.post(f"/quizzes/{quiz.id}/submit", json={
        "answers": [
            {"question_id": str(questions[0].id), "selected_option": "A"},
            {"question_id": str(questions[1].id), "selected_option": "B"},
        ]
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["score"] == 100
    assert data["passed"] is True
    assert data["total_questions"] == 2


async def test_submit_quiz_partial(client: AsyncClient, db: AsyncSession):
    quiz, questions = await _create_quiz_with_questions(db)
    resp = await client.post(f"/quizzes/{quiz.id}/submit", json={
        "answers": [
            {"question_id": str(questions[0].id), "selected_option": "A"},
            {"question_id": str(questions[1].id), "selected_option": "C"},  # wrong
        ]
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["score"] == 50
    assert data["passed"] is True  # passing_score is 50


async def test_submit_quiz_failing(client: AsyncClient, db: AsyncSession):
    quiz, questions = await _create_quiz_with_questions(db)
    # Set passing score to 70 by creating a new quiz
    quiz2 = make_quiz(questions[0].quiz_id, passing_score=70)
    # Actually use existing quiz which has passing_score=50,
    # submit all wrong answers
    resp = await client.post(f"/quizzes/{quiz.id}/submit", json={
        "answers": [
            {"question_id": str(questions[0].id), "selected_option": "D"},
            {"question_id": str(questions[1].id), "selected_option": "D"},
        ]
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["score"] == 0
    assert data["passed"] is False


async def test_submit_quiz_not_found(client: AsyncClient):
    resp = await client.post(f"/quizzes/{uuid.uuid4()}/submit", json={
        "answers": [
            {"question_id": str(uuid.uuid4()), "selected_option": "A"},
        ]
    })
    assert resp.status_code == 404


async def test_submit_quiz_invalid_option(client: AsyncClient, db: AsyncSession):
    quiz, questions = await _create_quiz_with_questions(db)
    resp = await client.post(f"/quizzes/{quiz.id}/submit", json={
        "answers": [
            {"question_id": str(questions[0].id), "selected_option": "Z"},
        ]
    })
    assert resp.status_code == 422
