from datetime import datetime
from pydantic import BaseModel, Field

class FIRResponse(BaseModel):
    id: str = Field(..., alias="_id")
    fir_number: str
    clone_id: str
    detection_id: str
    registration_number: str
    vehicle_brand: str
    vehicle_model: str
    vehicle_color: str
    vehicle_type: str
    owner_name: str
    offense: str
    sections: str
    location: str
    reported_date: datetime
    risk_score: float
    risk_level: str
    status: str

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
