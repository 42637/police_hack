from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logging import logger

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB: {} ...", settings.MONGODB_URL)
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client[settings.DATABASE_NAME]
    logger.info("Successfully connected to MongoDB database: {}", settings.DATABASE_NAME)
    await ensure_indexes()

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")

async def get_database():
    return db_instance.db

async def ensure_indexes():
    """Ensure database collections are properly indexed for performance."""
    if db_instance.db is None:
        return
    
    db = db_instance.db
    logger.info("Ensuring indexes on collections...")
    
    # 1. users
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    
    # 2. registered_vehicles
    await db.registered_vehicles.create_index("registration_number", unique=True)
    
    # 3. detections
    await db.detections.create_index("location")
    await db.detections.create_index("upload_time")
    await db.detections.create_index("risk_score")
    
    # 4. detected_vehicles
    await db.detected_vehicles.create_index("detection_id")
    await db.detected_vehicles.create_index("number_plate")
    await db.detected_vehicles.create_index("is_flagged_clone")
    
    # 5. cloned_vehicles
    await db.cloned_vehicles.create_index("detection_id")
    await db.cloned_vehicles.create_index("number_plate")
    await db.cloned_vehicles.create_index("risk_score")
    await db.cloned_vehicles.create_index("verified_status")
    
    # 6. chat_history
    await db.chat_history.create_index("user_id")
    await db.chat_history.create_index("session_id")
    
    # 7. audit_logs
    await db.audit_logs.create_index("user_id")
    await db.audit_logs.create_index("timestamp")
    
    logger.info("Collection indexing completed successfully.")
