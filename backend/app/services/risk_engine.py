from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from app.core.logging import logger

# Distance matrix between key centers for spatial-temporal intelligence (in Kilometers)
DISTANCES = {
    ("vijayawada", "hyderabad"): 270,
    ("hyderabad", "vijayawada"): 270,
    ("vijayawada", "guntur"): 35,
    ("guntur", "vijayawada"): 35,
    ("guntur", "hyderabad"): 280,
    ("hyderabad", "guntur"): 280,
    ("vijayawada", "vizag"): 350,
    ("vizag", "vijayawada"): 350,
    ("hyderabad", "vizag"): 620,
    ("vizag", "hyderabad"): 620,
}

def get_distance(loc1: str, loc2: str) -> float:
    """Helper to look up or estimate distance between two locations in KM."""
    l1 = loc1.lower()
    l2 = loc2.lower()
    
    # Check exact key matches
    for key, dist in DISTANCES.items():
        if key[0] in l1 and key[1] in l2:
            return dist
            
    # Default fallback distance if location names are arbitrary
    if l1 == l2:
        return 0.0
    return 150.0 # Default estimated distance between checkpoints

class RiskEngine:
    @staticmethod
    async def analyze_risk(
        db, 
        number_plate: str, 
        detected_attrs: Dict[str, Any], 
        current_location: str,
        current_time: datetime
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Runs the risk engine comparing detected vehicle features against registered database
        and analyzing historical travel logs. Returns: (risk_score, risk_level, details)
        """
        logger.info("Risk Engine evaluating plate: {} at Location: {}", number_plate, current_location)
        
        # Initialize risk factors
        risk_score = 0.0
        mismatch_details = {}
        is_clone = False

        # 1. Look up the vehicle in the registered database
        reg_vehicle = await db.registered_vehicles.find_one({"registration_number": number_plate})
        
        if not reg_vehicle:
            # Unregistered plate detection is an warning but not necessarily a clone (might be out-of-state)
            risk_score += 25.0
            mismatch_details["registration"] = {
                "status": "UNREGISTERED",
                "message": f"Vehicle plate '{number_plate}' not found in registry database."
            }
        else:
            # Vehicle is registered, check for visual attribute mismatches
            reg_brand = reg_vehicle["vehicle_brand"]
            reg_model = reg_vehicle["vehicle_model"]
            reg_color = reg_vehicle["vehicle_color"]
            reg_status = "Wanted" if reg_vehicle.get("is_blacklisted") else "Active"

            det_brand = detected_attrs.get("brand", "")
            det_model = detected_attrs.get("model", "")
            det_color = detected_attrs.get("color", "")

            # Check Brand Mismatch
            if reg_brand.lower() != det_brand.lower():
                risk_score += 35.0
                is_clone = True
                mismatch_details["brand"] = {
                    "registered": reg_brand,
                    "detected": det_brand,
                    "mismatch": True
                }

            # Check Model Mismatch
            if reg_model.lower() != det_model.lower():
                risk_score += 35.0
                is_clone = True
                mismatch_details["model"] = {
                    "registered": reg_model,
                    "detected": det_model,
                    "mismatch": True
                }

            # Check Color Mismatch
            if reg_color.lower() != det_color.lower():
                risk_score += 20.0
                is_clone = True
                mismatch_details["color"] = {
                    "registered": reg_color,
                    "detected": det_color,
                    "mismatch": True
                }

            # Check Vehicle Type Mismatch
            reg_type = reg_vehicle.get("vehicle_type", "car")
            det_type = detected_attrs.get("vehicle_type", "car")
            if reg_type.lower() != det_type.lower():
                risk_score += 40.0
                is_clone = True
                mismatch_details["vehicle_type"] = {
                    "registered": reg_type,
                    "detected": det_type,
                    "mismatch": True
                }

            # Check Registry status flag
            if reg_status in ["Wanted", "Suspended"]:
                risk_score += 30.0
                mismatch_details["registry_status"] = {
                    "status": reg_status,
                    "message": f"Vehicle registered status is flagged as {reg_status}."
                }

        # 2. Check for Impossible Travel Time (Spatial-Temporal Mismatch)
        # Look for detections of the same plate in the past 24 hours
        time_limit = current_time - timedelta(hours=24)
        
        # Query past detections of this plate
        if number_plate and len(number_plate.strip()) >= 3:
            cursor = db.detected_vehicles.find({
                "number_plate": number_plate,
                "detection_id": {"$ne": None} # valid links
            })
            
            async for prev_det_veh in cursor:
                # Look up parent detection details (location & time)
                from bson import ObjectId
                try:
                    prev_det_id = ObjectId(prev_det_veh["detection_id"]) if isinstance(prev_det_veh["detection_id"], str) else prev_det_veh["detection_id"]
                except Exception:
                    prev_det_id = prev_det_veh["detection_id"]
                    
                prev_det = await db.detections.find_one({"_id": prev_det_id})
                if not prev_det and isinstance(prev_det_id, ObjectId):
                    prev_det = await db.detections.find_one({"_id": str(prev_det_id)})
                elif not prev_det and isinstance(prev_det_id, str):
                    try:
                        prev_det = await db.detections.find_one({"_id": ObjectId(prev_det_id)})
                    except Exception:
                        pass
                if not prev_det:
                    continue

                prev_time = prev_det["upload_time"]
                prev_location = prev_det["location"]
                
                # Avoid comparing against the current record itself if already stored
                if prev_time >= current_time:
                    continue
                    
                time_diff = (current_time - prev_time).total_seconds()
                if time_diff <= 0:
                    continue
                    
                distance = get_distance(prev_location, current_location)
                if distance == 0:
                    continue # same checkpoint
                    
                # Speed = distance in KM / time in hours
                speed_kmh = (distance / time_diff) * 3600.0
                
                # If the calculated speed to travel between the locations exceeds 180 km/h,
                # we classify it as impossible travel (likely clones operating in parallel).
                if speed_kmh > 180.0:
                    risk_score = 100.0 # Force absolute maximum risk
                    is_clone = True
                    time_diff_mins = time_diff / 60.0
                    mismatch_details["spatial_temporal"] = {
                        "type": "impossible_travel",
                        "previous_location": prev_location,
                        "current_location": current_location,
                        "previous_time": prev_time.isoformat(),
                        "current_time": current_time.isoformat(),
                        "time_difference_mins": round(time_diff_mins, 2),
                        "distance_km": distance,
                        "implied_speed_kmh": round(speed_kmh, 2),
                        "message": f"Impossible Travel: Detected at {prev_location} and {current_location} within {time_diff_mins:.1f} mins (Implied Speed: {speed_kmh:.0f} km/h)."
                    }
                    break

        # Max out risk score at 100
        risk_score = min(risk_score, 100.0)

        # Categorize Risk Level
        if risk_score >= 80.0:
            risk_level = "Critical"
        elif risk_score >= 50.0:
            risk_level = "High"
        elif risk_score >= 20.0:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # If flagged clone but risk score is high/critical, ensure details log is set
        if is_clone and not mismatch_details:
            mismatch_details["general"] = {
                "message": "Flagged clone due to cumulative visual and database scoring indicators."
            }

        logger.info("Analysis complete for {}: Risk Score = {}, Level = {}", number_plate, risk_score, risk_level)
        return risk_score, risk_level, mismatch_details
