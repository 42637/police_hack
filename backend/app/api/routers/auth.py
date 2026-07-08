from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from app.database.session import get_database
from app.models.user import UserResponse, Token, UserLogin
from app.api.deps import get_current_user
from app.core.logging import logger
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    # 1. Look up user by username
    user = await db.users.find_one({"username": form_data.username})
    if not user:
        logger.warning("Failed login attempt: user '{}' not found", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        logger.warning("Failed login attempt: incorrect password for user '{}'", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Enforce Only Admin Login
    if user.get("role") != "Admin":
        logger.warning("Access denied: user '{}' is role '{}' (Admin required)", form_data.username, user.get("role"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden. Only Admin accounts can access this platform."
        )

    # 4. Generate JWT access token
    access_token = create_access_token(
        subject=str(user["_id"]),
        role=user["role"]
    )
    
    # Serialize object ID
    user["_id"] = str(user["_id"])
    
    # 5. Create Audit Log
    client_host = request.client.host if request.client else "unknown"
    audit_log = {
        "user_id": user["_id"],
        "action": "USER_LOGIN",
        "details": f"Admin login successful for user: {user['username']}",
        "ip_address": client_host,
        "timestamp": datetime.utcnow()
    }
    await db.audit_logs.insert_one(audit_log)
    
    logger.info("Admin user logged in: {} from IP {}", user["username"], client_host)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
