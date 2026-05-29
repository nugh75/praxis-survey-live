"""Tabelle: una risposta-questionario (Response) con N risposte-item (Answer)."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _now():
    return datetime.now(timezone.utc)


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    questionnaire: Mapped[str] = mapped_column(String(32), index=True)  # studenti|insegnanti
    lang: Mapped[str] = mapped_column(String(5), default="it")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    answers: Mapped[list["Answer"]] = relationship(
        back_populates="response", cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    response_id: Mapped[int] = mapped_column(ForeignKey("responses.id", ondelete="CASCADE"), index=True)
    question_key: Mapped[str] = mapped_column(String(64), index=True)
    dimension: Mapped[str] = mapped_column(String(16), index=True)
    # Un solo campo valorizzato a seconda del tipo:
    value_num: Mapped[float | None] = mapped_column(Float, nullable=True)   # likert / number
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)     # text / single / boolean

    response: Mapped["Response"] = relationship(back_populates="answers")


Index("ix_answers_q_dim", Answer.question_key, Answer.dimension)
