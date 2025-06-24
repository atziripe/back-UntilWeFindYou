from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class RiskAssessmentBase(BaseModel):
    case_id: UUID
    risk_level: str  # 'low', 'high'
    model_version: Optional[str]

class RiskAssessmentCreate(RiskAssessmentBase):
    pass

class RiskAssessmentRead(RiskAssessmentBase):
    id: UUID
    evaluated_at: datetime

    class Config:
        orm_mode = True
