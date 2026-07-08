from fastapi import APIRouter, Depends, HTTPException, status
from app.database.session import get_database
from app.api.deps import get_admin_user
from app.models.clone import ClonedVehicleResponse, ClonedVehicleUpdate
from app.core.logging import logger
from datetime import datetime
from bson import ObjectId
from typing import Optional

router = APIRouter(prefix="/clones", tags=["Clone Alerts Manager"])

@router.get("")
async def list_cloned_vehicles(
    page: int = 1,
    limit: int = 10,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    skip = (page - 1) * limit
    query_filter = {}
    if risk_level:
        query_filter["risk_level"] = risk_level
    if status:
        query_filter["verified_status"] = status

    cursor = db.cloned_vehicles.find(query_filter).sort("created_at", -1).skip(skip).limit(limit)
    clones = []
    async for c in cursor:
        c["_id"] = str(c["_id"])
        
        # Join registry owner data if possible
        reg = await db.registered_vehicles.find_one({"registration_number": c["number_plate"]})
        if reg:
            c["registered_owner"] = reg["owner_name"]
            c["registered_brand"] = reg["vehicle_brand"]
            c["registered_model"] = reg["vehicle_model"]
            c["registered_color"] = reg["vehicle_color"]
            c["registered_type"] = reg.get("vehicle_type", "car")
            c["registered_status"] = "Wanted" if reg.get("is_blacklisted") else "Active"

        # Join detection frame details
        det = None
        if c.get("detection_id"):
            try:
                det = await db.detections.find_one({"_id": ObjectId(c["detection_id"])})
            except Exception:
                pass
            if not det:
                det = await db.detections.find_one({"_id": str(c["detection_id"])})
        if det:
            c["location"] = det["location"]
            c["frame_path"] = det["frame_path"]
            c["upload_time"] = det["upload_time"]
            
        # Join detected vehicle crop path
        det_veh = None
        if c.get("detected_vehicle_id"):
            try:
                det_veh = await db.detected_vehicles.find_one({"_id": ObjectId(c["detected_vehicle_id"])})
            except Exception:
                pass
            if not det_veh:
                det_veh = await db.detected_vehicles.find_one({"_id": str(c["detected_vehicle_id"])})
        if det_veh:
            c["crop_path"] = det_veh["crop_path"]
            c["detected_brand"] = det_veh["brand"]
            c["detected_model"] = det_veh["model"]
            c["detected_color"] = det_veh["color"]
            c["detected_type"] = det_veh.get("vehicle_type", "car")

        clones.append(c)
        
    total = await db.cloned_vehicles.count_documents(query_filter)
    return {
        "clones": clones,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/{clone_id}")
async def get_clone_details(
    clone_id: str,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    try:
        obj_id = ObjectId(clone_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid clone ID format.")

    clone = await db.cloned_vehicles.find_one({"_id": obj_id})
    if not clone:
        raise HTTPException(status_code=404, detail="Clone alert record not found.")
        
    clone["_id"] = str(clone["_id"])
    
    # Enrich details (registered vs detected)
    reg = await db.registered_vehicles.find_one({"registration_number": clone["number_plate"]})
    if reg:
        clone["registered_vehicle"] = {
            "id": str(reg["_id"]),
            "number_plate": reg["registration_number"],
            "brand": reg["vehicle_brand"],
            "model": reg["vehicle_model"],
            "color": reg["vehicle_color"],
            "vehicle_type": reg.get("vehicle_type", "car"),
            "owner": reg["owner_name"],
            "status": "Wanted" if reg.get("is_blacklisted") else "Active"
        }
    
    det_veh = None
    if clone.get("detected_vehicle_id"):
        try:
            det_veh = await db.detected_vehicles.find_one({"_id": ObjectId(clone["detected_vehicle_id"])})
        except Exception:
            pass
        if not det_veh:
            det_veh = await db.detected_vehicles.find_one({"_id": str(clone["detected_vehicle_id"])})
    if det_veh:
        clone["detected_vehicle"] = {
            "id": str(det_veh["_id"]),
            "number_plate": det_veh["number_plate"],
            "brand": det_veh["brand"],
            "model": det_veh["model"],
            "color": det_veh["color"],
            "vehicle_type": det_veh.get("vehicle_type", "car"),
            "crop_path": det_veh["crop_path"],
            "plate_confidence": det_veh["plate_confidence"]
        }

    det = None
    if clone.get("detection_id"):
        try:
            det = await db.detections.find_one({"_id": ObjectId(clone["detection_id"])})
        except Exception:
            pass
        if not det:
            det = await db.detections.find_one({"_id": str(clone["detection_id"])})
    if det:
        clone["detection_details"] = {
            "id": str(det["_id"]),
            "video_name": det["video_name"],
            "video_path": det["video_path"],
            "frame_path": det["frame_path"],
            "location": det["location"],
            "upload_time": det["upload_time"]
        }

    return clone

@router.put("/{clone_id}")
async def update_clone_status(
    clone_id: str,
    payload: ClonedVehicleUpdate,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    try:
        obj_id = ObjectId(clone_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid clone ID format.")

    clone = await db.cloned_vehicles.find_one({"_id": obj_id})
    if not clone:
        raise HTTPException(status_code=404, detail="Clone alert record not found.")

    update_fields = {}
    if payload.verified_status is not None:
        update_fields["verified_status"] = payload.verified_status
    if payload.officer_notes is not None:
        update_fields["officer_notes"] = payload.officer_notes

    if update_fields:
        await db.cloned_vehicles.update_one({"_id": obj_id}, {"$set": update_fields})
        
        # Create audit log
        audit_log = {
            "user_id": current_user["_id"],
            "action": "REVIEW_CLONE",
            "details": f"Updated clone ticket {clone_id} ({clone['number_plate']}) status to '{payload.verified_status or clone['verified_status']}'",
            "ip_address": "unknown",
            "timestamp": datetime.utcnow()
        }
        await db.audit_logs.insert_one(audit_log)
        
        logger.info("Admin {} updated clone alert {} to status {}", 
                    current_user["username"], clone_id, payload.verified_status)

    return {"message": "Clone alert updated successfully."}
