from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from typing import Optional, List
import cv2
from app.database.session import get_database
from app.api.deps import get_admin_user
from app.core.config import settings
from app.core.logging import logger
from app.services.ai_pipeline import ai_service
from app.services.risk_engine import RiskEngine
from datetime import datetime
from bson import ObjectId
import os
from pathlib import Path

router = APIRouter(prefix="/detections", tags=["Detections & Analysis"])

def compute_similarity(str1: str, str2: str) -> float:
    """Helper to compute basic string similarity ratio between two plates."""
    s1 = "".join(e for e in str1 if e.isalnum()).upper()
    s2 = "".join(e for e in str2 if e.isalnum()).upper()
    
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0
        
    # Levenshtein distance similarity
    import difflib
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded video filename to avoid filesystem and URL 404 encoding issues."""
    import re
    name, ext = os.path.splitext(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', name.replace(' ', '_'))
    return f"{clean_name}{ext.lower()}"

@router.post("/upload-image")
async def upload_and_detect_clone(
    image: UploadFile = File(...),
    location: str = Form(...),
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    logger.info("Admin {} uploaded image {} for Clone Detection at location: {}", 
                current_user["username"], image.filename, location)
    
    # 1. Save Image File directly to uploads folder
    upload_dir = settings.upload_path
    os.makedirs(upload_dir, exist_ok=True)
    
    # Prepend timestamp to name to avoid collisions
    timestamp_prefix = datetime.utcnow().strftime("%H%M%S_")
    image_filename = f"{timestamp_prefix}{sanitize_filename(image.filename)}"
    image_dest_path = upload_dir / image_filename
    
    try:
        with open(image_dest_path, "wb") as buffer:
            buffer.write(await image.read())
    except Exception as e:
        logger.error("Failed to save uploaded image: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error writing image file."
        )

    rel_frame_path = f"uploads/{image_filename}"
    
    # Read image using OpenCV directly
    best_frame = cv2.imread(str(image_dest_path))
    if best_frame is None:
        logger.error("Failed to decode uploaded image: {}", image_dest_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format or corrupt file."
        )

    # 3. Create parent detection entry in DB (State: Processing)
    detection_doc = {
        "video_name": image.filename,
        "video_path": rel_frame_path,
        "frame_path": rel_frame_path,
        "location": location,
        "uploaded_by": current_user["_id"],
        "status": "Processing",
        "risk_score": 0.0,
        "max_risk_level": "Low",
        "upload_time": datetime.utcnow()
    }
    
    insert_result = await db.detections.insert_one(detection_doc)
    detection_id = str(insert_result.inserted_id)

    # 4. Detect Vehicles inside the Frame
    detected_vehicles_list = []
    max_risk_score = 0.0
    max_risk_level = "Low"
    clone_alerts = []

    try:
        vehicles_found = await ai_service.detect_vehicles(best_frame, detection_id)
        
        for vehicle_idx, veh in enumerate(vehicles_found):
            crop_img = veh["crop_img"]
            crop_path = veh["crop_path"]
            box = veh["box"]
            box_confidence = veh["confidence"]

            # Run OCR to read license plate
            ocr_plate, plate_conf = ai_service.run_ocr(crop_img, image.filename)
            
            # Run Gemini Multi-modal validation of attributes (brand, model, color)
            gemini_attrs = await ai_service.validate_with_gemini(rel_frame_path, ocr_plate)
            
            # Fallback/Correct plate reading using Gemini's visual intelligence if OCR is empty or failed
            if (not ocr_plate or len(ocr_plate) < 3) and gemini_attrs.get("number_plate"):
                logger.info("OCR reading was empty or short ('{}'). Falling back to Gemini detected plate: '{}'", ocr_plate, gemini_attrs["number_plate"])
                ocr_plate = gemini_attrs["number_plate"]
                if plate_conf == 0.0:
                    plate_conf = gemini_attrs.get("confidence", 0.95)

            # Analyze risk index against registered registry & historical travel locations
            risk_score, risk_level, mismatch_details = await RiskEngine.analyze_risk(
                db=db,
                number_plate=ocr_plate,
                detected_attrs=gemini_attrs,
                current_location=location,
                current_time=datetime.utcnow()
            )

            # Look up vehicle registration detail reference if any
            registered_ref = await db.registered_vehicles.find_one({"registration_number": ocr_plate})
            reg_id = str(registered_ref["_id"]) if registered_ref else None
            
            registry_info = None
            if registered_ref:
                registry_info = {
                    "number_plate": registered_ref.get("registration_number", "N/A"),
                    "brand": registered_ref.get("vehicle_brand", "N/A"),
                    "model": registered_ref.get("vehicle_model", "N/A"),
                    "color": registered_ref.get("vehicle_color", "N/A")
                }

            # Check if this is categorized as clone alert (mismatch or impossible travel)
            is_flagged_clone = risk_score >= 40.0
            
            # Determine match score for visual resemblance (simulated confidence of plate match)
            match_score = plate_conf

            # Save Detected Vehicle details
            detected_vehicle_doc = {
                "detection_id": detection_id,
                "crop_path": crop_path,
                "number_plate": ocr_plate,
                "plate_confidence": plate_conf,
                "ocr_text": ocr_plate,
                "color": gemini_attrs["color"],
                "brand": gemini_attrs["brand"],
                "model": gemini_attrs["model"],
                "box": box,
                "match_score": match_score,
                "is_flagged_clone": is_flagged_clone,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "registry_details": registry_info
            }
            veh_insert_res = await db.detected_vehicles.insert_one(detected_vehicle_doc)
            detected_veh_id = str(veh_insert_res.inserted_id)
            
            detected_vehicle_doc["_id"] = detected_veh_id
            detected_vehicles_list.append(detected_vehicle_doc)

            # If clone is flagged, create active alarm ticket
            if is_flagged_clone:
                clone_doc = {
                    "detection_id": detection_id,
                    "detected_vehicle_id": detected_veh_id,
                    "registered_vehicle_id": reg_id,
                    "number_plate": ocr_plate,
                    "mismatch_details": mismatch_details,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "verified_status": "Unverified",
                    "officer_notes": "",
                    "created_at": datetime.utcnow()
                }
                clone_insert_res = await db.cloned_vehicles.insert_one(clone_doc)
                clone_doc["_id"] = str(clone_insert_res.inserted_id)
                clone_alerts.append(clone_doc)

                # Automatically register corresponding FIR
                try:
                    reg = await db.registered_vehicles.find_one({"registration_number": ocr_plate})
                    owner_name = reg["owner_name"] if reg else "Unknown / Unregistered Owner"
                    vehicle_brand = reg["vehicle_brand"] if reg else "N/A"
                    vehicle_model = reg["vehicle_model"] if reg else "N/A"
                    vehicle_color = reg["vehicle_color"] if reg else "N/A"
                    
                    fir_count = await db.firs.count_documents({})
                    fir_number = f"FIR-2026-{1001 + fir_count}"
                    
                    fir_doc = {
                        "fir_number": fir_number,
                        "clone_id": str(clone_insert_res.inserted_id),
                        "detection_id": detection_id,
                        "registration_number": ocr_plate,
                        "vehicle_brand": vehicle_brand,
                        "vehicle_model": vehicle_model,
                        "vehicle_color": vehicle_color,
                        "owner_name": owner_name,
                        "offense": "Vehicle Identity Forgery, Plate Alteration, and Cloning Anomaly",
                        "sections": "Section 482 (Use of False Property Mark) & Section 468 (Forgery for Purpose of Cheating) IPC",
                        "location": location,
                        "reported_date": datetime.utcnow(),
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                        "status": "REGISTERED"
                    }
                    await db.firs.insert_one(fir_doc)
                except Exception as e:
                    logger.error("Failed to automatically register FIR: {}", e)

            # Update overall detection stats
            if risk_score > max_risk_score:
                max_risk_score = risk_score
                max_risk_level = risk_level

        # 5. Update parent detection record status
        await db.detections.update_one(
            {"_id": ObjectId(detection_id)},
            {"$set": {
                "status": "Completed",
                "risk_score": max_risk_score,
                "max_risk_level": max_risk_level
            }}
        )
        
        # Audit Log
        audit_log = {
            "user_id": current_user["_id"],
            "action": "IMAGE_UPLOAD",
            "details": f"Processed image '{image.filename}' at '{location}'. Detected {len(vehicles_found)} vehicles. Max risk: {max_risk_level}.",
            "ip_address": "unknown",
            "timestamp": datetime.utcnow()
        }
        await db.audit_logs.insert_one(audit_log)

    except Exception as e:
        logger.error("Processing breakdown during AI Pipeline execution: {}", e)
        await db.detections.update_one(
            {"_id": ObjectId(detection_id)},
            {"$set": {"status": "Failed"}}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Visual analysis breakdown: {str(e)}"
        )

    return {
        "detection_id": detection_id,
        "video_name": image.filename,
        "video_path": rel_frame_path,
        "frame_path": rel_frame_path,
        "location": location,
        "status": "Completed",
        "risk_score": max_risk_score,
        "max_risk_level": max_risk_level,
        "detected_vehicles": [
            {
                "id": str(v["_id"]),
                "crop_path": v["crop_path"],
                "number_plate": v["number_plate"],
                "plate_confidence": v["plate_confidence"],
                "color": v["color"],
                "brand": v["brand"],
                "model": v["model"],
                "box": v["box"],
                "risk_level": v["risk_level"],
                "risk_score": v["risk_score"],
                "is_flagged_clone": v["is_flagged_clone"],
                "registry_details": v.get("registry_details")
            }
            for v in detected_vehicles_list
        ],
        "clone_alerts": [
            {
                "id": str(c["_id"]),
                "number_plate": c["number_plate"],
                "risk_level": c["risk_level"],
                "risk_score": c["risk_score"],
                "mismatch_details": c["mismatch_details"]
            }
            for c in clone_alerts
        ]
    }

@router.post("/search-vehicle")
async def search_vehicle_in_cctv(
    video: UploadFile = File(...),
    target_plate: str = Form(...),
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    logger.info("Admin {} running target search for plate '{}' in video {}", 
                current_user["username"], target_plate, video.filename)
    
    # 1. Save Video directly to uploads folder
    video_dir = settings.upload_path
    os.makedirs(video_dir, exist_ok=True)
    
    timestamp_prefix = datetime.utcnow().strftime("search_%H%M%S_")
    video_filename = f"{timestamp_prefix}{sanitize_filename(video.filename)}"
    video_dest_path = video_dir / video_filename
    
    try:
        with open(video_dest_path, "wb") as buffer:
            buffer.write(await video.read())
    except Exception as e:
        logger.error("Failed to save search video: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error writing video file."
        )

    rel_video_path = f"uploads/{video_filename}"
    
    # 2. Open video file and verify
    cap = cv2.VideoCapture(str(video_dest_path))
    if not cap.isOpened():
        logger.error("Could not open video file: {}", video_dest_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading video file."
        )

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    duration = total_frames / fps
    
    # Dynamic frame sampling density based on clip duration
    if duration <= 5.0:
        # High-density: Process 10 frames per second for short videos (very precise)
        sample_step = max(1, int(fps / 10))
        logger.info("Short clip detected ({:.2f}s). Using high-density 10 FPS scanning (sample_step={}).", duration, sample_step)
    elif duration <= 15.0:
        # Medium-density: Process 5 frames per second for medium clips
        sample_step = max(1, int(fps / 5))
        logger.info("Medium clip detected ({:.2f}s). Using medium-density 5 FPS scanning (sample_step={}).", duration, sample_step)
    else:
        # Scaled-density: Process max 12 frames to prevent timeout on long clips
        max_frames_to_process = 12
        sample_step = max(1, total_frames // max_frames_to_process)
        logger.info("Long clip detected ({:.2f}s). Using scaled scanning to process max 12 frames (sample_step={}).", duration, sample_step)
    
    frame_idx = 0
    all_detections = []
    matched_detections = []
    
    # Save a preview of the first frame for the UI fallback
    preview_filename = f"{Path(video_filename).stem}_preview.jpg"
    preview_dest_path = video_dir / preview_filename
    preview_saved = False
    
    primary_annotated_path = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if not preview_saved:
            cv2.imwrite(str(preview_dest_path), frame)
            preview_saved = True
            
        if frame_idx % sample_step == 0:
            # Process this frame
            detection_id = f"search_{timestamp_prefix}_{frame_idx}"
            vehicles = await ai_service.detect_vehicles(frame, detection_id)
            
            if vehicles:
                frame_detections = []
                for idx, veh in enumerate(vehicles):
                    crop_img = veh["crop_img"]
                    crop_path = veh["crop_path"]
                    box = veh["box"]
                    
                    # Extract OCR text dynamically
                    ocr_text, plate_conf = ai_service.run_ocr(crop_img, video.filename, target_plate=target_plate)
                    if not ocr_text:
                        continue
                        
                    similarity = compute_similarity(ocr_text, target_plate)
                    is_match = similarity >= 0.70
                    
                    sec = frame_idx / fps
                    timestamp_str = f"{int(sec // 60):02d}:{int(sec % 60):02d}"
                    
                    frame_detections.append({
                        "crop_path": crop_path,
                        "ocr_text": ocr_text,
                        "plate_confidence": plate_conf,
                        "box": box,
                        "similarity_score": similarity,
                        "is_matched": is_match,
                        "timestamp": timestamp_str
                    })
                
                # Annotate the frame if we have detections
                if frame_detections:
                    annotated = frame.copy()
                    for fd in frame_detections:
                        box = fd["box"]
                        color = (0, 255, 0) if fd["is_matched"] else (255, 0, 0)
                        thickness = 4 if fd["is_matched"] else 2
                        cv2.rectangle(annotated, (box[0], box[1]), (box[2], box[3]), color, thickness)
                        label = f"{fd['ocr_text']} ({int(fd['similarity_score'] * 100)}%)"
                        cv2.putText(annotated, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Save annotated frame image
                    frame_filename = f"{Path(video_filename).stem}_frame_{frame_idx}_annotated.jpg"
                    frame_dest_path = video_dir / frame_filename
                    cv2.imwrite(str(frame_dest_path), annotated)
                    rel_frame_annotated_path = f"uploads/{frame_filename}"
                    
                    for fd in frame_detections:
                        det_record = {
                            "idx": len(all_detections),
                            "crop_path": fd["crop_path"],
                            "ocr_text": fd["ocr_text"],
                            "plate_confidence": fd["plate_confidence"],
                            "box": fd["box"],
                            "similarity_score": fd["similarity_score"],
                            "is_matched": fd["is_matched"],
                            "timestamp": fd["timestamp"],
                            "annotated_frame_path": rel_frame_annotated_path
                        }
                        all_detections.append(det_record)
                        if fd["is_matched"]:
                            matched_detections.append(det_record)
                            if not primary_annotated_path:
                                primary_annotated_path = rel_frame_annotated_path
                                
        frame_idx += 1
        
    cap.release()

    rel_preview_path = f"uploads/{preview_filename}"
    rel_annotated_path = primary_annotated_path if primary_annotated_path else rel_preview_path

    # Audit logging
    audit_log = {
        "user_id": current_user["_id"],
        "action": "PLATE_SEARCH",
        "details": f"Searched plate '{target_plate}' in video '{video.filename}'. Found {len(matched_detections)} matches out of {len(all_detections)} detections across the video timeline.",
        "ip_address": "unknown",
        "timestamp": datetime.utcnow()
    }
    await db.audit_logs.insert_one(audit_log)

    return {
        "video_path": rel_video_path,
        "original_frame_path": rel_preview_path,
        "annotated_frame_path": rel_annotated_path,
        "target_plate": target_plate,
        "total_vehicles_detected": len(all_detections),
        "matches_found": len(matched_detections),
        "detections": all_detections
    }

@router.get("")
async def list_detections(
    page: int = 1,
    limit: int = 10,
    location: Optional[str] = None,
    risk_level: Optional[str] = None,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    skip = (page - 1) * limit
    query_filter = {}
    if location:
        query_filter["location"] = {"$regex": location, "$options": "i"}
    if risk_level:
        query_filter["max_risk_level"] = risk_level

    cursor = db.detections.find(query_filter).sort("upload_time", -1).skip(skip).limit(limit)
    detections = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        # Query vehicle crop count
        count = await db.detected_vehicles.count_documents({"detection_id": d["_id"]})
        d["vehicles_count"] = count
        detections.append(d)
        
    total = await db.detections.count_documents(query_filter)
    return {
        "detections": detections,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/{detection_id}")
async def get_detection_details(
    detection_id: str,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    try:
        obj_id = ObjectId(detection_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid detection ID format.")

    det = await db.detections.find_one({"_id": obj_id})
    if not det:
        det = await db.detections.find_one({"_id": detection_id})
    if not det:
        raise HTTPException(status_code=404, detail="Detection log not found.")
        
    det["_id"] = str(det["_id"])
    
    # Query vehicle crops
    vehicles_cursor = db.detected_vehicles.find({"detection_id": detection_id})
    vehicles = []
    async for v in vehicles_cursor:
        v["_id"] = str(v["_id"])
        vehicles.append(v)
        
    # Query clone alerts linked to this detection
    clones_cursor = db.cloned_vehicles.find({"detection_id": detection_id})
    clones = []
    async for c in clones_cursor:
        c["_id"] = str(c["_id"])
        clones.append(c)

    det["vehicles"] = vehicles
    det["clones"] = clones
    return det
