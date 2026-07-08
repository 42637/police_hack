from fastapi import APIRouter, Depends, HTTPException, status
from app.database.session import get_database
from app.api.deps import get_admin_user
from app.models.vehicle import RegisteredVehicleCreate, RegisteredVehicleResponse
from app.core.logging import logger
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/vehicles", tags=["Registered Vehicles"])

@router.get("")
async def list_vehicles(
    page: int = 1,
    limit: int = 15,
    plate: Optional[str] = None,
    state: Optional[str] = None,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    skip = (page - 1) * limit
    query_filter = {}
    if plate:
        query_filter["registration_number"] = {"$regex": plate.upper(), "$options": "i"}
    if state:
        query_filter["registration_state"] = state

    cursor = db.registered_vehicles.find(query_filter).sort("created_at", -1).skip(skip).limit(limit)
    vehicles = []
    async for v in cursor:
        v["_id"] = str(v["_id"])
        vehicles.append(v)
        
    total = await db.registered_vehicles.count_documents(query_filter)
    return {
        "vehicles": vehicles,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/{plate}", response_model=RegisteredVehicleResponse)
async def get_vehicle_by_plate(
    plate: str,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    vehicle = await db.registered_vehicles.find_one({"registration_number": plate.upper()})
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle plate '{plate}' not found in registry database."
        )
    vehicle["_id"] = str(vehicle["_id"])
    return vehicle

@router.post("", response_model=RegisteredVehicleResponse)
async def register_vehicle(
    vehicle_in: RegisteredVehicleCreate,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    # Normalize plate
    plate_norm = vehicle_in.registration_number.replace(" ", "").upper()
    
    # Check if exists
    existing = await db.registered_vehicles.find_one({"registration_number": plate_norm})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this plate number is already registered."
        )
        
    vehicle_doc = vehicle_in.dict()
    vehicle_doc["registration_number"] = plate_norm
    vehicle_doc["created_at"] = datetime.utcnow()
    
    insert_res = await db.registered_vehicles.insert_one(vehicle_doc)
    vehicle_doc["_id"] = str(insert_res.inserted_id)
    
    # Audit log
    audit_log = {
        "user_id": current_user["_id"],
        "action": "REGISTER_VEHICLE",
        "details": f"Registered new vehicle: {plate_norm} ({vehicle_in.vehicle_color} {vehicle_in.vehicle_brand} {vehicle_in.vehicle_model})",
        "ip_address": "unknown",
        "timestamp": datetime.utcnow()
    }
    await db.audit_logs.insert_one(audit_log)
    
    return vehicle_doc
