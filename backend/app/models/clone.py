from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ClonedVehicleBase(BaseModel):
    detection_id: str
    detected_vehicle_id: str
    registered_vehicle_id: Optional[str] = None
    number_plate: str
    mismatch_details: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Details of mismatch, e.g. visual difference or spatial-temporal impossible travel"
    )
    risk_score: float
    risk_level: str # Low, Medium, High, Critical
    verified_status: str = Field(default="Unverified") # Unverified, VerifiedClone, FalseAlarm
    officer_notes: Optional[str] = ""

class ClonedVehicleCreate(ClonedVehicleBase):
    pass

class ClonedVehicleUpdate(BaseModel):
    verified_status: Optional[str] = None
    officer_notes: Optional[str] = None

class ClonedVehicleResponse(ClonedVehicleBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClonedVehicleInDB(ClonedVehicleBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
