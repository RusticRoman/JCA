import enum
import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AttendanceType(str, enum.Enum):
    LIVE = "LIVE"
    RECORDED = "RECORDED"


class VideoProgress(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "video_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uq_user_video"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("videos.id"), index=True)
    last_position_seconds: Mapped[int] = mapped_column(Integer, default=0)
    total_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(default=False)
    attendance_type: Mapped[AttendanceType] = mapped_column(default=AttendanceType.RECORDED)


class SubjectCompletion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Denormalized table for fast dashboard reads."""
    __tablename__ = "subject_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "subject_id", name="uq_user_subject"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), index=True)
    videos_completed: Mapped[int] = mapped_column(Integer, default=0)
    videos_total: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(default=False)
