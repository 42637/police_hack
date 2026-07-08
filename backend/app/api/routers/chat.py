from fastapi import APIRouter, Depends, HTTPException, status
from app.database.session import get_database
from app.api.deps import get_admin_user
from app.services.chat_assistant import chat_assistant
from app.core.logging import logger
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/chat", tags=["Police AI Assistant"])

class ChatRequest(BaseModel):
    query: str
    session_id: str

@router.post("")
async def query_assistant(
    payload: ChatRequest,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    user_id = str(current_user["_id"])
    logger.info("Admin {} sent query in session '{}'", current_user["username"], payload.session_id)
    
    # 1. Fetch or create chat session
    session = await db.chat_history.find_one({
        "user_id": user_id,
        "session_id": payload.session_id
    })
    
    if not session:
        session = {
            "user_id": user_id,
            "session_id": payload.session_id,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        insert_res = await db.chat_history.insert_one(session)
        session["_id"] = str(insert_res.inserted_id)
    else:
        session["_id"] = str(session["_id"])

    # 2. Append User Message
    user_message = {
        "role": "user",
        "content": payload.query,
        "timestamp": datetime.utcnow()
    }
    
    # 3. Call Chat Assistant Service
    try:
        assistant_res = await chat_assistant.handle_query(db, payload.query, user_id)
    except Exception as e:
        logger.error("Chat assistant pipeline error: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating AI Assistant response."
        )

    assistant_message = {
        "role": "assistant",
        "content": assistant_res["content"],
        "metadata": assistant_res["metadata"],
        "timestamp": datetime.utcnow()
    }

    # 4. Save to DB
    updated_messages = session.get("messages", [])
    updated_messages.append(user_message)
    updated_messages.append(assistant_message)
    
    await db.chat_history.update_one(
        {"_id": ObjectId(session["_id"])},
        {"$set": {
            "messages": updated_messages,
            "updated_at": datetime.utcnow()
        }}
    )

    return {
        "session_id": payload.session_id,
        "response": assistant_res["content"],
        "metadata": assistant_res["metadata"]
    }

@router.get("/sessions")
async def get_chat_sessions(
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    user_id = str(current_user["_id"])
    cursor = db.chat_history.find({"user_id": user_id}).sort("updated_at", -1)
    sessions = []
    async for s in cursor:
        s["_id"] = str(s["_id"])
        # Return summary description based on first user query
        first_query = "New Session"
        for m in s.get("messages", []):
            if m["role"] == "user":
                first_query = m["content"]
                break
        
        # Limit preview to 40 characters
        if len(first_query) > 40:
            first_query = first_query[:37] + "..."
            
        sessions.append({
            "session_id": s["session_id"],
            "title": first_query,
            "updated_at": s["updated_at"]
        })
    return sessions

@router.get("/sessions/{session_id}")
async def get_session_history(
    session_id: str,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    user_id = str(current_user["_id"])
    session = await db.chat_history.find_one({
        "user_id": user_id,
        "session_id": session_id
    })
    
    if not session:
        return {"session_id": session_id, "messages": []}
        
    session["_id"] = str(session["_id"])
    return session
from bson import ObjectId
