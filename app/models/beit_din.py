import enum
import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"


class Case(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "beit_din_cases"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    rabbi_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[CaseStatus] = mapped_column(default=CaseStatus.OPEN)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")

    notes: Mapped[list["CaseNote"]] = relationship(back_populates="case", lazy="selectin")
    documents: Mapped[list["CaseDocument"]] = relationship(back_populates="case", lazy="selectin")


class CaseNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "case_notes"

    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("beit_din_cases.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)

    case: Mapped["Case"] = relationship(back_populates="notes")


class CaseDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "case_documents"

    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("beit_din_cases.id"))
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(String(255))
    gcs_path: Mapped[str] = mapped_column(String(512))

    case: Mapped["Case"] = relationship(back_populates="documents")
