import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Program(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "programs"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    year: Mapped[int] = mapped_column(Integer, default=1)  # 1=standard, 2=advanced/graduate

    semesters: Mapped[list["Semester"]] = relationship(back_populates="program", lazy="selectin")


class Semester(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "semesters"

    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id"))
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")

    program: Mapped["Program"] = relationship(back_populates="semesters")
    subjects: Mapped[list["Subject"]] = relationship(back_populates="semester", lazy="selectin")


class Subject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subjects"

    semester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("semesters.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)

    semester: Mapped["Semester"] = relationship(back_populates="subjects")
    videos: Mapped[list["Video"]] = relationship(back_populates="subject", lazy="selectin")


class Video(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "videos"

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    gcs_path: Mapped[str] = mapped_column(String(512), default="")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    order: Mapped[int] = mapped_column(Integer, default=0)

    subject: Mapped["Subject"] = relationship(back_populates="videos")
