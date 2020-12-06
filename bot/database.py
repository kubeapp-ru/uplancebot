from config import settings
from motor.motor_asyncio import AsyncIOMotorClient


mongo_client = AsyncIOMotorClient(settings.DB_HOST,
                                  settings.DB_PORT,
                                  maxPoolSize=settings.DB_MAX_POOL_SIZE)
db = mongo_client[settings.DB_NAME]