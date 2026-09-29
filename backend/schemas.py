from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class TelemetryCreate(BaseModel):
    stage_id: int
    detected_objects: List[Any]  
    calculated_volume: float


class StageResponse(BaseModel):
    id: int
    name: str
    nlp_stage_id: Optional[str]
    target_volume: float
    current_volume: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: int
    name: str
    stages: List[StageResponse] = []

    class Config:
        from_attributes = True