import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Quiz(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quizzes"

    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("videos.id"))
    title: Mapped[str] = mapped_column(String(255))
    passing_score: Mapped[int] = mapped_column(Integer, default=70)

    questions: Mapped[list["Question"]] = relationship(back_populates="quiz", lazy="selectin")


class Question(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id"))
    text: Mapped[str] = mapped_column(Text)
    option_a: Mapped[str] = mapped_column(String(500))
    option_b: Mapped[str] = mapped_column(String(500))
    option_c: Mapped[str] = mapped_column(String(500))
    option_d: Mapped[str] = mapped_column(String(500))
    correct_option: Mapped[str] = mapped_column(String(1))  # A, B, C, or D
    order: Mapped[int] = mapped_column(Integer, default=0)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")


class QuizAttempt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quiz_attempts"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)

    answers: Mapped[list["Answer"]] = relationship(back_populates="attempt", lazy="selectin")


class Answer(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "answers"

    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quiz_attempts.id"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"))
    selected_option: Mapped[str] = mapped_column(String(1))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    attempt: Mapped["QuizAttempt"] = relationship(back_populates="answers")
