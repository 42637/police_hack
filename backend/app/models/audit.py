from datetime import datetime
from pydantic import BaseModel, Field

class AuditLogBase(BaseModel):
    user_id: str
    action: str # USER_LOGIN, DETECT_VIDEO, REVIEW_CLONE, etc.
    details: str
    ip_address: str

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: str = Field(..., alias="_id")
    timestamp: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AuditLogInDB(AuditLogBase):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
