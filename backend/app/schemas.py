"""Pydantic schemas per validazione I/O."""
from pydantic import BaseModel, Field


class AnswerIn(BaseModel):
    question_key: str
    value: str | float | int | bool | None = None


class ResponseIn(BaseModel):
    questionnaire: str = Field(pattern="^(studenti|insegnanti)$")
    lang: str = "it"
    answers: list[AnswerIn]


class ResponseOut(BaseModel):
    id: int
    questionnaire: str
    submitted_at: str
