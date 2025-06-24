from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime

class CaseBase(BaseModel):
    name: str
    photo_url: Optional[str]
    age: Optional[int]
    date_birth: date
    place_birth: str
    gender: str  # 'male', 'female', 'non-binary', ''ther'
    distinctive_features: Optional[str]
    eyes_color: str
    hair_description: str
    complexion: str
    weight: float
    height: float
    date_missing: datetime
    last_seen_location: Optional[str]
    forced_dissapearence: bool
    description: Optional[str]
    status: Optional[str] = "open"  # 'open', 'resolved', 'archived'
    reporting_entity_contact: Optional[str]
    relatives_contact: Optional[str]
    help_files : Optional[str]
    reported_by: Optional[str]
    created_at: datetime

class CaseCreate(CaseBase):
    pass

class CaseRead(CaseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
