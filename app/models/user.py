import enum
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    RABBI = "RABBI"
    TEACHER = "TEACHER"
    BEIT_DIN = "BEIT_DIN"
    ADMIN = "ADMIN"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[UserRole] = mapped_column(default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(default=True)
    hebrew_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enrollment_semester: Mapped[int] = mapped_column(default=1)
    program_year: Mapped[int] = mapped_column(default=1)

    # Self-referential: which mentor (RABBI/TEACHER) is this student assigned to
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    mentor: Mapped["User | None"] = relationship(
        "User", remote_side="User.id", back_populates="students", lazy="selectin"
    )
    students: Mapped[list["User"]] = relationship(
        "User", back_populates="mentor", lazy="selectin"
    )
