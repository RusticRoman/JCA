import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Answer, Question, Quiz, QuizAttempt


async def get_quiz(db: AsyncSession, quiz_id: uuid.UUID) -> Quiz | None:
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    return result.scalar_one_or_none()


async def grade_quiz(
    db: AsyncSession,
    quiz_id: uuid.UUID,
    user_id: uuid.UUID,
    submissions: list[dict],
) -> QuizAttempt:
    """Grade a quiz submission and return the attempt record."""
    quiz = await get_quiz(db, quiz_id)
    if not quiz:
        raise ValueError("Quiz not found")

    # Build question lookup
    question_map: dict[uuid.UUID, Question] = {q.id: q for q in quiz.questions}
    total = len(quiz.questions)
    correct = 0

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=user_id,
        total_questions=total,
    )
    db.add(attempt)
    await db.flush()

    for sub in submissions:
        question = question_map.get(sub["question_id"])
        if not question:
            continue
        is_correct = sub["selected_option"].upper() == question.correct_option.upper()
        if is_correct:
            correct += 1

        answer = Answer(
            attempt_id=attempt.id,
            question_id=sub["question_id"],
            selected_option=sub["selected_option"],
            is_correct=is_correct,
        )
        db.add(answer)

    score_pct = int((correct / total) * 100) if total > 0 else 0
    attempt.score = score_pct
    attempt.passed = score_pct >= quiz.passing_score

    await db.commit()
    await db.refresh(attempt)
    return attempt
