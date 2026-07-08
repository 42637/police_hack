from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.database.session import get_database
from app.core.logging import logger
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        user = await db.users.find_one({"_id": user_id}) # Fallback if stored as string
        
    if user is None:
        raise credentials_exception
        
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    # Serialize ObjectId for easy usage in handlers
    user["_id"] = str(user["_id"])
    return user

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Enforce only admin login/access policy."""
    if current_user.get("role") != "Admin":
        logger.warning("Unauthorized access attempt by user: {} with role: {}", current_user.get("username"), current_user.get("role"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted. Admin permission required."
        )
    return current_user
