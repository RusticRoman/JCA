from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Resource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "resources"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="general")
    gcs_path: Mapped[str] = mapped_column(String(512))
    filename: Mapped[str] = mapped_column(String(255))


class FAQ(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "faqs"

    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(default=0)
    is_published: Mapped[bool] = mapped_column(default=True)
