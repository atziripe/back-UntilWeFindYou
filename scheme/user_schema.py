from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str  # 'admin', 'ong', 'viewer'

class UserCreate(UserBase):
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

class UserRead(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
