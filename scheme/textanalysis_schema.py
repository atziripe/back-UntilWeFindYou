from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TextAnalysisBase(BaseModel):
    case_id: UUID
    danger_dectect: bool
    toxic: bool
    severe_toxic: bool
    obscene: bool
    threat: bool
    insult: bool
    identity_hate: bool
    confidence_score: float
    model_version: Optional[str]

class TextAnalysisCreate(TextAnalysisBase):
    pass

class CommentInput(BaseModel):
    text: str

class TextAnalysisRead(TextAnalysisBase):
    id: UUID
    evaluated_at: datetime

    class Config:
        orm_mode = True
