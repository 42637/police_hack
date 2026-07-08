from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class RegisteredVehicleBase(BaseModel):
    registration_number: str = Field(..., description="Normalized plate string")
    vehicle_brand: str
    vehicle_model: str
    vehicle_color: str
    registration_state: str
    registration_city: str
    owner_name: str
    is_blacklisted: bool = Field(default=False)
    crime_history_count: int = Field(default=0)

class RegisteredVehicleCreate(RegisteredVehicleBase):
    pass

class RegisteredVehicleResponse(RegisteredVehicleBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
class RegisteredVehicleInDB(RegisteredVehicleBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
