import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.logging import logger
import os
import cv2
import numpy as np

async def seed_database():
    logger.info("Starting database seeding...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # 1. Seed Users (Only Admin Login is allowed)
    logger.info("Seeding Admin User...")
    await db.users.delete_many({})
    admin_user = {
        "username": "admin",
        "email": "admin@sentinel.ai",
        "hashed_password": get_password_hash("admin123"),
        "role": "Admin",
        "full_name": "Cyber Intelligence Administrator",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.users.insert_one(admin_user)
    logger.info("Admin user seeded: admin / admin123")

    # 2. Seed Registered Vehicles
    logger.info("Seeding Registered Vehicles...")
    try:
        await db.registered_vehicles.drop_indexes()
    except Exception:
        pass
    await db.registered_vehicles.delete_many({})
    vehicles = [
        {
            "registration_number": "AP31CV1234",
            "vehicle_brand": "Maruti",
            "vehicle_model": "Swift",
            "vehicle_color": "Red",
            "registration_state": "Andhra Pradesh",
            "registration_city": "Vijayawada",
            "owner_name": "K. Venkatesh",
            "is_blacklisted": False,
            "crime_history_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=365)
        },
        {
            "registration_number": "TS09EX5678",
            "vehicle_brand": "Toyota",
            "vehicle_model": "Fortuner",
            "vehicle_color": "White",
            "registration_state": "Telangana",
            "registration_city": "Hyderabad",
            "owner_name": "M. Suresh Reddy",
            "is_blacklisted": True,
            "crime_history_count": 2,
            "created_at": datetime.utcnow() - timedelta(days=200)
        },
        {
            "registration_number": "AP16BY9999",
            "vehicle_brand": "Hyundai",
            "vehicle_model": "Creta",
            "vehicle_color": "Black",
            "registration_state": "Andhra Pradesh",
            "registration_city": "Vijayawada",
            "owner_name": "A. Seshagiri",
            "is_blacklisted": True,
            "crime_history_count": 1,
            "created_at": datetime.utcnow() - timedelta(days=150)
        },
        {
            "registration_number": "KA03MX4321",
            "vehicle_brand": "Honda",
            "vehicle_model": "City",
            "vehicle_color": "Silver",
            "registration_state": "Karnataka",
            "registration_city": "Bengaluru",
            "owner_name": "Priya Sharma",
            "is_blacklisted": False,
            "crime_history_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=500)
        },
        {
            "registration_number": "DL01CZ8888",
            "vehicle_brand": "BMW",
            "vehicle_model": "3 Series",
            "vehicle_color": "Blue",
            "registration_state": "Delhi",
            "registration_city": "New Delhi",
            "owner_name": "Vikram Malhotra",
            "is_blacklisted": False,
            "crime_history_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=120)
        }
    ]
    await db.registered_vehicles.insert_many(vehicles)
    logger.info("Registered vehicles seeded successfully.")

    # 3. Seed Prior Detections (to support Impossible Travel Time testing)
    logger.info("Seeding historical detections...")
    await db.detections.delete_many({})
    await db.detected_vehicles.delete_many({})
    await db.cloned_vehicles.delete_many({})
    await db.chat_history.delete_many({})
    await db.audit_logs.delete_many({})

    # Historic detection at Vijayawada
    historic_time = datetime.utcnow() - timedelta(minutes=2)
    detection_id = "60c72b2f9b1d8b2d88888888" # fixed object ID for linking
    
    historic_det = {
        "_id": detection_id,
        "video_name": "vijayawada_cctv_01.mp4",
        "video_path": "uploads/vijayawada_cctv_01.mp4",
        "frame_path": "uploads/vijayawada_cctv_01.jpg",
        "location": "Vijayawada Checkpoint Alpha",
        "uploaded_by": "system",
        "status": "Completed",
        "risk_score": 10.0,
        "max_risk_level": "Low",
        "upload_time": historic_time
    }
    await db.detections.insert_one(historic_det)

    historic_veh = {
        "detection_id": detection_id,
        "crop_path": "uploads/vijayawada_cctv_01_crop1.jpg",
        "number_plate": "AP31CV1234",
        "plate_confidence": 0.98,
        "ocr_text": "AP31CV1234",
        "color": "Red",
        "brand": "Maruti",
        "model": "Swift",
        "box": [100, 150, 400, 350],
        "match_score": 1.0,
        "is_flagged_clone": False,
        "risk_level": "Low",
        "risk_score": 10.0
    }
    await db.detected_vehicles.insert_one(historic_veh)
    
    # 4. Generate dummy media files physically to prevent 404 errors in the UI
    logger.info("Creating dummy files on disk...")
    upload_dir = settings.upload_path
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create black image with overlay text representing surveillance
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_img, "Vijayawada Checkpoint Alpha", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(str(upload_dir / "vijayawada_cctv_01.jpg"), dummy_img)
    
    # Create crop vehicle dummy image
    dummy_crop = np.zeros((200, 300, 3), dtype=np.uint8)
    cv2.putText(dummy_crop, "AP31CV1234", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(str(upload_dir / "vijayawada_cctv_01_crop1.jpg"), dummy_crop)
    
    # Create dummy 1-second video
    video_path = str(upload_dir / "vijayawada_cctv_01.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 10.0, (640, 480))
    for _ in range(10):
        out.write(dummy_img)
    out.release()
    
    logger.info("Database seeding completed.")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
