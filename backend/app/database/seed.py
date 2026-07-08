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
            "vehicle_type": "car",
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
            "vehicle_type": "car",
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
            "vehicle_type": "car",
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
            "vehicle_type": "car",
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
            "vehicle_type": "car",
            "registration_state": "Delhi",
            "registration_city": "New Delhi",
            "owner_name": "Vikram Malhotra",
            "is_blacklisted": False,
            "crime_history_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=120)
        },
        {
            "registration_number": "AP07BK2222",
            "vehicle_brand": "Royal Enfield",
            "vehicle_model": "Classic 350",
            "vehicle_color": "Black",
            "vehicle_type": "motorcycle",
            "registration_state": "Andhra Pradesh",
            "registration_city": "Guntur",
            "owner_name": "P. Ramesh Kumar",
            "is_blacklisted": False,
            "crime_history_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=50)
        },
        {
            "registration_number": "TS08TR8888",
            "vehicle_brand": "Tata",
            "vehicle_model": "Prima",
            "vehicle_color": "Yellow",
            "vehicle_type": "truck",
            "registration_state": "Telangana",
            "registration_city": "Hyderabad",
            "owner_name": "G. Satish Transport",
            "is_blacklisted": False,
            "crime_history_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=90)
        },
        {
            "registration_number": "AP26BS7777",
            "vehicle_brand": "Volvo",
            "vehicle_model": "9400",
            "vehicle_color": "White",
            "vehicle_type": "bus",
            "registration_state": "Andhra Pradesh",
            "registration_city": "Nellore",
            "owner_name": "Sri Krishna Travels",
            "is_blacklisted": False,
            "crime_history_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=180)
        }
    ]
    await db.registered_vehicles.insert_many(vehicles)
    logger.info("Registered vehicles seeded successfully.")

    # 3. Seed Prior Detections (to support Impossible Travel Time testing)
    logger.info("Seeding historical detections...")
    await db.detections.delete_many({})
    await db.detected_vehicles.delete_many({})
    await db.cloned_vehicles.delete_many({})
    await db.firs.delete_many({})
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
        "vehicle_type": "car",
        "box": [100, 150, 400, 350],
        "match_score": 1.0,
        "is_flagged_clone": False,
        "risk_level": "Low",
        "risk_score": 10.0
    }
    await db.detected_vehicles.insert_one(historic_veh)

    # Seed a clone alert and an FIR
    guntur_time = datetime.utcnow() - timedelta(minutes=5)
    guntur_det_id = "60c72b2f9b1d8b2d99999999"
    guntur_det = {
        "_id": guntur_det_id,
        "video_name": "guntur_cctv_02.mp4",
        "video_path": "uploads/guntur_cctv_02.mp4",
        "frame_path": "uploads/guntur_cctv_02.jpg",
        "location": "Guntur National Highway",
        "uploaded_by": "system",
        "status": "Completed",
        "risk_score": 85.0,
        "max_risk_level": "High",
        "upload_time": guntur_time
    }
    await db.detections.insert_one(guntur_det)

    guntur_veh_id = "60c72b2f9b1d8b2d77777777"
    guntur_veh = {
        "_id": guntur_veh_id,
        "detection_id": guntur_det_id,
        "crop_path": "uploads/guntur_cctv_02_crop1.jpg",
        "number_plate": "TS09EX5678",
        "plate_confidence": 0.95,
        "ocr_text": "TS09EX5678",
        "color": "Blue",
        "brand": "Hyundai",
        "model": "i20",
        "vehicle_type": "car",
        "box": [120, 160, 420, 360],
        "match_score": 0.3,
        "is_flagged_clone": True,
        "risk_level": "High",
        "risk_score": 85.0
    }
    await db.detected_vehicles.insert_one(guntur_veh)

    clone_id = "60c72b2f9b1d8b2d55555555"
    mismatch_details = {
        "brand": {"registered": "Toyota", "detected": "Hyundai", "mismatch": True},
        "model": {"registered": "Fortuner", "detected": "i20", "mismatch": True},
        "color": {"registered": "White", "detected": "Blue", "mismatch": True},
        "registry_status": {"status": "Wanted", "message": "Vehicle registered status is flagged as Wanted."}
    }
    guntur_clone = {
        "_id": clone_id,
        "detection_id": guntur_det_id,
        "detected_vehicle_id": guntur_veh_id,
        "registered_vehicle_id": None,
        "number_plate": "TS09EX5678",
        "mismatch_details": mismatch_details,
        "risk_score": 85.0,
        "risk_level": "High",
        "verified_status": "Unverified",
        "officer_notes": "",
        "created_at": guntur_time
    }
    await db.cloned_vehicles.insert_one(guntur_clone)

    guntur_fir = {
        "fir_number": "FIR-2026-1001",
        "clone_id": clone_id,
        "detection_id": guntur_det_id,
        "registration_number": "TS09EX5678",
        "vehicle_brand": "Toyota",
        "vehicle_model": "Fortuner",
        "vehicle_color": "White",
        "vehicle_type": "car",
        "owner_name": "M. Suresh Reddy",
        "offense": "Vehicle Identity Forgery, Plate Alteration, and Cloning Anomaly",
        "sections": "Section 482 (Use of False Property Mark) & Section 468 (Forgery for Purpose of Cheating) IPC",
        "location": "Guntur National Highway",
        "reported_date": guntur_time,
        "risk_score": 85.0,
        "risk_level": "High",
        "status": "REGISTERED"
    }
    await db.firs.insert_one(guntur_fir)
    
    # 4. Generate dummy media files physically to prevent 404 errors in the UI
    logger.info("Creating dummy files on disk...")
    upload_dir = settings.upload_path
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create black image with overlay text representing surveillance (Vijayawada)
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_img, "Vijayawada Checkpoint Alpha", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(str(upload_dir / "vijayawada_cctv_01.jpg"), dummy_img)
    
    # Create crop vehicle dummy image (Vijayawada)
    dummy_crop = np.zeros((200, 300, 3), dtype=np.uint8)
    cv2.putText(dummy_crop, "AP31CV1234", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(str(upload_dir / "vijayawada_cctv_01_crop1.jpg"), dummy_crop)
    
    # Create dummy 1-second video (Vijayawada)
    video_path = str(upload_dir / "vijayawada_cctv_01.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 10.0, (640, 480))
    for _ in range(10):
        out.write(dummy_img)
    out.release()

    # Create black image with overlay text representing surveillance (Guntur)
    dummy_img_guntur = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_img_guntur, "Guntur National Highway", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(str(upload_dir / "guntur_cctv_02.jpg"), dummy_img_guntur)
    
    # Create crop vehicle dummy image (Guntur)
    dummy_crop_guntur = np.zeros((200, 300, 3), dtype=np.uint8)
    cv2.putText(dummy_crop_guntur, "TS09EX5678", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(str(upload_dir / "guntur_cctv_02_crop1.jpg"), dummy_crop_guntur)
    
    # Create dummy 1-second video (Guntur)
    video_path_guntur = str(upload_dir / "guntur_cctv_02.mp4")
    out_guntur = cv2.VideoWriter(video_path_guntur, fourcc, 10.0, (640, 480))
    for _ in range(10):
        out_guntur.write(dummy_img_guntur)
    out_guntur.release()
    
    logger.info("Database seeding completed.")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
