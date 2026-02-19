import enum
import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FieldType(str, enum.Enum):
    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    SELECT = "SELECT"
    RATING = "RATING"


class MonthlyQuestionnaire(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "monthly_questionnaires"
    __table_args__ = (
        Index("ix_questionnaire_active_year_month", "is_active", "year", "month"),
    )

    title: Mapped[str] = mapped_column(String(255))
    month: Mapped[int] = mapped_column(Integer)  # 1-12
    year: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True)

    fields: Mapped[list["QuestionnaireField"]] = relationship(
        back_populates="questionnaire", lazy="selectin", cascade="all, delete-orphan"
    )


class QuestionnaireField(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "questionnaire_fields"

    questionnaire_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monthly_questionnaires.id")
    )
    label: Mapped[str] = mapped_column(String(500))
    field_type: Mapped[FieldType] = mapped_column(default=FieldType.TEXT)
    options: Mapped[str] = mapped_column(Text, default="")  # JSON for SELECT type
    order: Mapped[int] = mapped_column(Integer, default=0)
    required: Mapped[bool] = mapped_column(default=True)

    questionnaire: Mapped["MonthlyQuestionnaire"] = relationship(back_populates="fields")


class QuestionnaireResponse(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "questionnaire_responses"
    __table_args__ = (
        Index("ix_response_questionnaire_user", "questionnaire_id", "user_id"),
    )

    questionnaire_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monthly_questionnaires.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    answers: Mapped[str] = mapped_column(Text, default="{}")  # JSON
