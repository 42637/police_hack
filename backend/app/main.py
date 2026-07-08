from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import logger
from app.database.session import connect_to_mongo, close_mongo_connection
from app.api.routers import auth, dashboard, detections, clones, chat, vehicles, firs
import os
from datetime import datetime

app = FastAPI(
    title="Sentinel AI API",
    description="Enterprise-grade AI Powered Vehicle Intelligence & Clone Detection Platform Services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Mount Static Uploads Folder (Serve videos, frames, and crops to frontend)
os.makedirs(settings.upload_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(settings.upload_path)), name="uploads")

# Include Router paths under /api
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(detections.router, prefix="/api")
app.include_router(clones.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")
app.include_router(firs.router, prefix="/api")

from fastapi.responses import JSONResponse, RedirectResponse

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
