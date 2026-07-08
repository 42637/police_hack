from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger
import json

class ChatAssistantService:
    def __init__(self):
        self.gemini_configured = False
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_configured = True
            except Exception as e:
                logger.error("Failed to configure Gemini for Chat Assistant: {}", e)

    async def handle_query(self, db, query: str, user_id: str) -> Dict[str, Any]:
        """
        Parses user intent, extracts factual data from MongoDB,
        and uses Gemini to construct a response with structured rendering metadata.
        """
        logger.info("Chat assistant parsing query: '{}'", query)
        query_lower = query.lower()
        
        # 1. Determine Intent & Query MongoDB
        context_data = []
        metadata = None
        data_type = "text"

        # Check for Cloned / Suspicious vehicles
        if "clone" in query_lower or "suspicious" in query_lower or "fake" in query_lower:
            cursor = db.cloned_vehicles.find({}).sort("created_at", -1).limit(10)
            clones = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                # Also lookup registration details
                reg = await db.registered_vehicles.find_one({"registration_number": doc["number_plate"]})
                if reg:
                    doc["owner"] = reg["owner_name"]
                    doc["registered_details"] = f"{reg['vehicle_color']} {reg['vehicle_brand']} {reg['vehicle_model']}"
                clones.append(doc)
                
            context_data = clones
            data_type = "clones_list"
            metadata = {
                "type": "table",
                "columns": ["number_plate", "risk_level", "risk_score", "verified_status", "details"],
                "data": [
                    {
                        "id": c["_id"],
                        "number_plate": c["number_plate"],
                        "risk_level": c["risk_level"],
                        "risk_score": c["risk_score"],
                        "verified_status": c["verified_status"],
                        "details": c["mismatch_details"].get("spatial_temporal", {}).get("message") or \
                                   c["mismatch_details"].get("brand", {}).get("message") or \
                                   f"Visual mismatch detected on {c['number_plate']}"
                    }
                    for c in clones
                ]
            }

        # Check for Detections Today
        elif "today" in query_lower or "recent" in query_lower or "uploads" in query_lower:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cursor = db.detections.find({"upload_time": {"$gte": today_start}}).sort("upload_time", -1).limit(10)
            detections = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                # Query associated detected vehicles
                vehicles_cursor = db.detected_vehicles.find({"detection_id": doc["_id"]})
                vehicles = []
                async for v in vehicles_cursor:
                    v["_id"] = str(v["_id"])
                    vehicles.append(v)
                doc["vehicles"] = vehicles
                detections.append(doc)
                
            context_data = detections
            data_type = "detections_list"
            
            flat_vehicles = []
            for d in detections:
                for v in d["vehicles"]:
                    flat_vehicles.append({
                        "id": v["_id"],
                        "time": d["upload_time"].strftime("%H:%M:%S"),
                        "location": d["location"],
                        "number_plate": v["number_plate"],
                        "risk_level": v["risk_level"],
                        "ocr_text": v["ocr_text"]
                    })
                    
            metadata = {
                "type": "table",
                "columns": ["time", "location", "number_plate", "risk_level", "ocr_text"],
                "data": flat_vehicles
            }

        # Check for Vehicles by Location
        elif "hyderabad" in query_lower or "vijayawada" in query_lower or "guntur" in query_lower or "vizag" in query_lower:
            target_loc = ""
            for loc in ["hyderabad", "vijayawada", "guntur", "vizag"]:
                if loc in query_lower:
                    target_loc = loc
                    break
                    
            # Use regex to find location
            cursor = db.detections.find({"location": {"$regex": target_loc, "$options": "i"}}).sort("upload_time", -1).limit(10)
            detections = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                # Query associated detected vehicles
                vehicles_cursor = db.detected_vehicles.find({"detection_id": doc["_id"]})
                vehicles = []
                async for v in vehicles_cursor:
                    v["_id"] = str(v["_id"])
                    vehicles.append(v)
                doc["vehicles"] = vehicles
                detections.append(doc)
                
            context_data = detections
            data_type = "location_list"
            
            flat_vehicles = []
            for d in detections:
                for v in d["vehicles"]:
                    flat_vehicles.append({
                        "id": v["_id"],
                        "location": d["location"],
                        "number_plate": v["number_plate"],
                        "vehicle_details": f"{v['color']} {v['brand']} {v['model']}",
                        "risk_level": v["risk_level"]
                    })
                    
            metadata = {
                "type": "table",
                "columns": ["location", "number_plate", "vehicle_details", "risk_level"],
                "data": flat_vehicles
            }

        # Check for Stats / Counts
        elif "count" in query_lower or "statistic" in query_lower or "summary" in query_lower or "chart" in query_lower:
            total_registered = await db.registered_vehicles.count_documents({})
            total_detections = await db.detections.count_documents({})
            total_clones = await db.cloned_vehicles.count_documents({})
            critical_clones = await db.cloned_vehicles.count_documents({"risk_level": "Critical"})
            high_clones = await db.cloned_vehicles.count_documents({"risk_level": "High"})
            
            stats = {
                "total_registered_vehicles": total_registered,
                "total_detections_logged": total_detections,
                "total_cloned_alerts": total_clones,
                "risk_breakdown": {
                    "Critical": critical_clones,
                    "High": high_clones,
                    "Medium": await db.cloned_vehicles.count_documents({"risk_level": "Medium"}),
                    "Low": await db.cloned_vehicles.count_documents({"risk_level": "Low"})
                }
            }
            context_data = [stats]
            data_type = "stats"
            
            metadata = {
                "type": "chart",
                "chart_type": "bar",
                "data": [
                    {"name": "Critical", "value": critical_clones},
                    {"name": "High", "value": high_clones},
                    {"name": "Medium", "value": stats["risk_breakdown"]["Medium"]},
                    {"name": "Low", "value": stats["risk_breakdown"]["Low"]}
                ]
            }

        # Generic Database Query Search for attributes (e.g. Color or Brand)
        else:
            # Check for color matching
            colors = ["red", "blue", "black", "white", "silver"]
            detected_color = None
            for c in colors:
                if c in query_lower:
                    detected_color = c.capitalize()
                    break
                    
            # Check for brand matching
            brands = ["maruti", "toyota", "hyundai", "honda", "bmw"]
            detected_brand = None
            for b in brands:
                if b in query_lower:
                    detected_brand = b.capitalize()
                    break

            mongo_query = {}
            if detected_color:
                mongo_query["color"] = detected_color
            if detected_brand:
                mongo_query["brand"] = detected_brand

            if mongo_query:
                cursor = db.detected_vehicles.find(mongo_query).limit(10)
                vehicles = []
                async for v in cursor:
                    v["_id"] = str(v["_id"])
                    vehicles.append(v)
                context_data = vehicles
                data_type = "attributes_search"
                metadata = {
                    "type": "table",
                    "columns": ["number_plate", "brand", "model", "color", "risk_level"],
                    "data": [
                        {
                            "id": v["_id"],
                            "number_plate": v["number_plate"],
                            "brand": v["brand"],
                            "model": v["model"],
                            "color": v["color"],
                            "risk_level": v["risk_level"]
                        }
                        for v in vehicles
                    ]
                }

        # If still empty, get last 5 general logs
        if not context_data:
            cursor = db.detections.find({}).sort("upload_time", -1).limit(5)
            dets = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                dets.append(doc)
            context_data = dets
            data_type = "general_detections"
            metadata = {
                "type": "table",
                "columns": ["video_name", "location", "upload_time", "max_risk_level"],
                "data": [
                    {
                        "id": d["_id"],
                        "video_name": d["video_name"],
                        "location": d["location"],
                        "upload_time": d["upload_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "max_risk_level": d["max_risk_level"]
                    }
                    for d in dets
                ]
            }

        # 2. Formulate LLM Response using Gemini
        factual_str = json.dumps(context_data, default=str)
        
        system_instruction = (
            "You are Sentinel AI Cyber Intelligence Assistant, an elite assistant helping officers analyze vehicle clones and detections.\n"
            "Respond ONLY using facts from the provided database query records below. Do not make up or hallucinate any vehicles, license plates, or names.\n"
            "If the data records do not contain what was asked, state clearly: 'No matching records were found in the active intelligence databases.'\n"
            "Format your answer formally in clean, professional markdown tables or bullet points where appropriate."
        )

        prompt = f"{system_instruction}\n\nUser Query: {query}\n\nDatabase Query Results:\n{factual_str}"

        if self.gemini_configured:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = await asyncio.to_thread(model.generate_content, prompt)
                content = response.text.strip()
            except Exception as e:
                logger.error("Gemini Assistant Query error: {}", e)
                content = self.generate_fallback_response(query_lower, context_data, data_type)
        else:
            content = self.generate_fallback_response(query_lower, context_data, data_type)

        return {
            "content": content,
            "metadata": metadata
        }

    def generate_fallback_response(self, query: str, data: list, data_type: str) -> str:
        """Fallback rule-based text generator if Gemini is not configured or fails."""
        if not data or len(data) == 0:
            return "### Operational Log\nNo matching records were found in the active intelligence databases."

        if data_type == "clones_list":
            res = "### Active Clone Alerts\n\n| Number Plate | Risk Level | Score | Status | Details |\n|---|---|---|---|---|\n"
            for c in data:
                detail = c["mismatch_details"].get("spatial_temporal", {}).get("message") or "Visual mismatch"
                res += f"| **{c['number_plate']}** | {c['risk_level']} | {c['risk_score']}% | {c['verified_status']} | {detail} |\n"
            return res

        elif data_type == "stats":
            s = data[0]
            return (
                f"### System Statistics Summary\n\n"
                f"- **Registered Vehicles in Database**: {s['total_registered_vehicles']}\n"
                f"- **Total Video Intelligence Detections**: {s['total_detections_logged']}\n"
                f"- **Active Cloned Plate Alerts**: {s['total_cloned_alerts']}\n"
                f"  - *Critical Level Alert*: {s['risk_breakdown']['Critical']}\n"
                f"  - *High Level Alert*: {s['risk_breakdown']['High']}\n"
                f"  - *Medium Level Alert*: {s['risk_breakdown']['Medium']}\n"
            )

        else:
            res = "### Vehicle Detections Query Results\n\n"
            for d in data:
                if "video_name" in d:
                    res += f"- **Video**: `{d['video_name']}` | **Location**: {d['location']} | **Risk**: {d['max_risk_level']}\n"
                elif "number_plate" in d:
                    res += f"- **Plate**: `{d['number_plate']}` | **Visual**: {d.get('color')} {d.get('brand')} {d.get('model')} | **Risk**: {d['risk_level']}\n"
            return res

chat_assistant = ChatAssistantService()
import asyncio
from typing import Dict
