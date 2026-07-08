from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class DetectionBase(BaseModel):
    video_name: str
    video_path: str
    frame_path: Optional[str] = None
    location: str
    uploaded_by: str
    status: str = Field(default="Processing") # Processing, Completed, Failed
    risk_score: float = Field(default=0.0)
    max_risk_level: str = Field(default="Low") # Low, Medium, High, Critical

class DetectionCreate(BaseModel):
    video_name: str
    video_path: str
    location: str
    uploaded_by: str

class DetectionResponse(DetectionBase):
    id: str = Field(..., alias="_id")
    upload_time: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DetectionInDB(DetectionBase):
    upload_time: datetime = Field(default_factory=datetime.utcnow)

class DetectedVehicleBase(BaseModel):
    detection_id: str
    crop_path: Optional[str] = None
    number_plate: str
    plate_confidence: float
    ocr_text: str
    color: str
    brand: str
    model: str
    vehicle_type: str = "car"
    box: List[int] = Field(default_factory=list) # [x1, y1, x2, y2]
    match_score: float = 0.0
    is_flagged_clone: bool = False
    risk_level: str = "Low"
    risk_score: float = 0.0

class DetectedVehicleCreate(DetectedVehicleBase):
    pass

class DetectedVehicleResponse(DetectedVehicleBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
