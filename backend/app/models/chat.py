from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Rich UI components to render (e.g. {type: 'table', data: [...]})"
    )

class ChatSessionBase(BaseModel):
    user_id: str
    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)

class ChatSessionCreate(BaseModel):
    session_id: str

class ChatSessionResponse(ChatSessionBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatSessionInDB(ChatSessionBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
