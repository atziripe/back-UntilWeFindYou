from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DashboardMetricBase(BaseModel):
    metric_name: str
    metric_value: float

class DashboardMetricCreate(DashboardMetricBase):
    pass

class DashboardMetricRead(DashboardMetricBase):
    id: UUID
    calculated_at: datetime

    class Config:
        orm_mode = True
