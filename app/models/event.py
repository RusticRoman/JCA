import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EventType(str, enum.Enum):
    RETREAT = "RETREAT"
    SHABBATON = "SHABBATON"
    HOLIDAY = "HOLIDAY"
    CLASS = "CLASS"
    OTHER = "OTHER"


class Event(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    event_type: Mapped[EventType] = mapped_column(default=EventType.OTHER)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String(255), default="")
    capacity: Mapped[int] = mapped_column(Integer, default=0)  # 0 = unlimited
    google_calendar_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    registrations: Mapped[list["EventRegistration"]] = relationship(
        back_populates="event", lazy="selectin", cascade="all, delete-orphan"
    )


class EventRegistration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "event_registrations"
    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_user"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    event: Mapped["Event"] = relationship(back_populates="registrations")
